#!/usr/bin/env python3
"""Render validated, finite-molecule MaterialsScript jobs from JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


MULTIPLICITIES = {
    1: "Singlet",
    2: "Doublet",
    3: "Triplet",
    4: "Quartet",
    5: "Quintet",
}


def perl_quote(value: object) -> str:
    text = str(value).replace("\\", "/").replace("'", "\\'")
    return f"'{text}'"


def yes_no(value: bool) -> str:
    return '"Yes"' if value else '"No"'


def render_dmol3(data: dict) -> str:
    method = data.get("method", {})
    inputs = data.get("inputs", [])
    if not inputs:
        raise ValueError("inputs must contain at least one structure")
    rows = []
    for entry in inputs:
        multiplicity = int(entry.get("multiplicity", 1))
        if multiplicity not in MULTIPLICITIES:
            raise ValueError(f"unsupported multiplicity: {multiplicity}")
        rows.append(
            "    { name => %s, file => %s, charge => %d, multiplicity => %s },"
            % (
                perl_quote(entry["name"]),
                perl_quote(entry["file"]),
                int(entry.get("charge", 0)),
                perl_quote(MULTIPLICITIES[multiplicity]),
            )
        )
    quality = method.get("quality", "Medium")
    functional = method.get("functional", "PBE")
    basis = method.get("basis_file", "4.4")
    core = method.get("core_treatment", "All Electron")
    max_scf = int(method.get("max_scf_cycles", 220))
    dispersion = bool(method.get("dispersion", True))
    optimize = bool(method.get("geometry_opt", False))
    potential = bool(method.get("calculate_potential", True))
    field_mode = '"Field"' if potential else '"None"'
    solvent = method.get("solvent")
    cosmo_lines = (
        f'            UseCosmo => "Yes",\n            CosmoSolvent => {perl_quote(solvent)},\n'
        if solvent
        else '            UseCosmo => "No",\n'
    )
    return f"""#!perl
use strict;
use warnings;
use MaterialsScript qw(:all);

Documents->SaveAllAtEnd = "Yes";
print "MS_TASK_START\\n";
open(my $out, ">", "ms_results.csv") or die "Cannot write ms_results.csv: $!";
print $out "name,stage,total_energy,HOMO_eV,LUMO_eV,gap_eV,status,message\\n";

my @cases = (
{chr(10).join(rows)}
);

for my $case (@cases) {{
    my $name = $case->{{name}};
    my $file = $case->{{file}};
    my $doc = $Documents{{$file}};
    if (!$doc) {{
        print $out "$name,load,,,,,failed,cannot load $file\\n";
        next;
    }}
    my $settings = Settings(
            Quality => {perl_quote(quality)},
            ElectronicQuality => {perl_quote(quality)},
            TheoryLevel => "GGA",
            NonLocalFunctional => {perl_quote(functional)},
            BasisFile => {perl_quote(basis)},
            CoreTreatment => {perl_quote(core)},
            Charge => $case->{{charge}},
            Multiplicity => $case->{{multiplicity}},
            UseSmearing => "No",
            MaximumSCFCycles => {max_scf},
            SCFConvergence => "1e-005",
            UseDFTD => {yes_no(dispersion)},
            DFTDMethod => "Grimme",
{cosmo_lines}            PopulationAnalysis => "Mulliken",
            CalculateCharge => "Mulliken",
            CalculateBondOrder => "Mulliken",
            CalculateChargeDensity => {field_mode},
            CalculatePotential => {field_mode}
    );
    eval {{
        Modules->DMol3->ChangeSettings($settings);
        if ({1 if optimize else 0}) {{
            my $opt = Modules->DMol3->GeometryOptimization->Run($doc, $settings);
            $doc->SaveAs("$name.dmol3_opt.xsd");
            print "DMOL3_OPT_DONE $name\\n";
        }}
        my $sp = Modules->DMol3->Energy->Run($doc, $settings);
        my $energy = eval {{ $sp->TotalEnergy }} // "";
        my $homo = eval {{ $sp->HOMOEnergy }} // "";
        my $lumo = eval {{ $sp->LUMOEnergy }} // "";
        my $gap = ($homo ne "" && $lumo ne "") ? $lumo - $homo : "";
        print $out "$name,dmol3_sp,$energy,$homo,$lumo,$gap,ok,\\n";
        print "DMOL3_SP_DONE $name\\n";
        1;
    }} or do {{
        my $err = $@;
        $err =~ s/[\\r\\n,]+/ /g;
        print $out "$name,dmol3_sp,,,,,failed,$err\\n";
        print "DMOL3_SP_FAILED $name $err\\n";
    }};
}}
close $out;
print "MS_TASK_ALL_DONE\\n";
"""


def render_forcite(data: dict) -> str:
    inputs = data.get("inputs", [])
    if not inputs:
        raise ValueError("inputs must contain at least one structure")
    method = data.get("method", {})
    forcefield = method.get("forcefield", "COMPASSIII")
    quality = method.get("quality", "Fine")
    max_iterations = int(method.get("max_iterations", 7000))
    rows = [
        "    { name => %s, file => %s },"
        % (perl_quote(entry["name"]), perl_quote(entry["file"]))
        for entry in inputs
    ]
    return f"""#!perl
use strict;
use warnings;
use MaterialsScript qw(:all);

Documents->SaveAllAtEnd = "Yes";
print "MS_TASK_START\\n";
open(my $out, ">", "ms_results.csv") or die "Cannot write ms_results.csv: $!";
print $out "name,stage,potential_energy,status,message\\n";
my @cases = (
{chr(10).join(rows)}
);
my $settings = Settings(
    CurrentForcefield => {perl_quote(forcefield)},
    ChargeAssignment => "Forcefield assigned",
    Quality => {perl_quote(quality)},
    MaxIterations => {max_iterations},
    UseMaxEnergy => "Yes",
    MaxEnergy => 1e-5,
    UseMaxForce => "Yes",
    MaxForce => 0.005,
    UseMaxDisplacement => "Yes",
    MaxDisplacement => 1e-4
);
for my $case (@cases) {{
    my $name = $case->{{name}};
    my $file = $case->{{file}};
    my $doc = $Documents{{$file}};
    if (!$doc) {{
        print $out "$name,load,,failed,cannot load $file\\n";
        next;
    }}
    eval {{
        Modules->Forcite->ChangeSettings($settings);
        Modules->Forcite->GeometryOptimization->Run($doc, $settings);
        $doc->SaveAs("$name.forcite_opt.xsd");
        my $energy = eval {{ $doc->PotentialEnergy }} // "";
        print $out "$name,forcite_opt,$energy,ok,\\n";
        print "FORCITE_OPT_DONE $name\\n";
        1;
    }} or do {{
        my $err = $@;
        $err =~ s/[\\r\\n,]+/ /g;
        print $out "$name,forcite_opt,,failed,$err\\n";
        print "FORCITE_OPT_FAILED $name $err\\n";
    }};
}}
close $out;
print "MS_TASK_ALL_DONE\\n";
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    data = json.loads(Path(args.manifest).read_text(encoding="utf-8-sig"))
    task_type = data.get("task_type")
    if task_type in {"dmol3-frontier", "dmol3-single-point"}:
        content = render_dmol3(data)
    elif task_type == "forcite-opt":
        content = render_forcite(data)
    else:
        raise SystemExit(
            "Supported task_type values: dmol3-frontier, dmol3-single-point, forcite-opt"
        )
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8", newline="\n")
    print(json.dumps({"output": str(output.resolve()), "task_type": task_type}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
