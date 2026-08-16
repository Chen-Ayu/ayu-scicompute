# Example requests

## Open molecular workflow

> 使用开源后端检查这个木质素片段的结构、电荷和多重度，优化后计算HOMO、LUMO、能隙、Mulliken电荷、电子密度和MEP cube。必须给出收敛证据、方法、单位、原始文件索引和局限性。

## Binding cycle

> 对添加剂A、木质素片段B和复合物AB采用相同方法、基组、溶剂模型和电荷约定计算结合能。说明片段采用独立优化还是复合物冻结几何，并评估BSSE需求。

## User-licensed polymer workflow

> 为聚合物、溶剂和离子建立无定形胞，完成最小化、升温、NPT密度平衡和生产MD，然后分析密度、RDF、氢键和回转半径。如果没有经过用户授权的可用后端，只准备脚本并标记prepared。

## Chat-only boundary

> 当前环境没有本机终端。只生成任务合同、输入模板和我需要手动执行的命令，不要声称计算已经运行。

## Transition-metal complex

> 比较一个过渡金属配合物的候选氧化态和自旋态，先检查电子数、自旋多重度、相对论处理和多参考风险，再选择当前可用的ORCA流程；所有比较保持方法和参考态一致。

## Periodic-metal roadmap boundary

> 为体相金属建立结构弛豫、磁序、能带和DOS计算计划。当前版本应识别VASP路线并生成planned/prepared合同，但在VASP适配器、合法程序与POTCAR均未验证时不得声称运行。
