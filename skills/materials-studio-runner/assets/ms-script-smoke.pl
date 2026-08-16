#!perl
use strict;
use warnings;
use MaterialsScript qw(:all);

Documents->SaveAllAtEnd = "Yes";
print "MS_TASK_START\n";
my $doc = Documents->New("ms_skill_smoke.xsd");
my $o = $doc->CreateAtom("O", Point(X => 0.000000, Y => 0.000000, Z => 0.000000));
my $h1 = $doc->CreateAtom("H", Point(X => 0.758602, Y => 0.000000, Z => 0.504284));
my $h2 = $doc->CreateAtom("H", Point(X => -0.758602, Y => 0.000000, Z => 0.504284));
$doc->CreateBond($o, $h1, "Single");
$doc->CreateBond($o, $h2, "Single");
$doc->Save;
open(my $out, ">", "ms_results.csv") or die "Cannot write ms_results.csv: $!";
print $out "name,stage,status,message\n";
print $out "water,script_smoke,ok,\n";
close $out;
print "MS_TASK_ALL_DONE\n";
