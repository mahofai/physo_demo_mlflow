# PhySO

### 简介

使用RNN对数据点生成多条latex公式进行物理回归

输入：

一个带数据点及单位的csv，

输出：

一个scv，生成多个latex公式及公式各项系数，以及公式的打分。 由于模型评估页面背后的log_metric 不支持输入公式，所以需要在平台的日志中进行查看结果


### csv格式规范

参考输入为mechanical.csv：

x_name:z,x_name:vz,y_name:E,free_const:m,free_const:g,fix_const:const

"[1, 0, 0]","[1, -1, 0]","[2, -2, 1]","[0, 0, 1]","[1, -2, 0]","[0, 0, 0]"

-6.225153514337833,3.650977062068705,-71.51530639913841,,,1

-8.061125154909156,-7.628976755434175,-31.196610274732166,,,1

-9.101492871859389,-8.019623387980694,-37.32040628876261,,,1


x_name: 自变量名称
y_name: 因变量名称（只可以指定一个column）
free_const：可变参数名称
fix_const：固定参数名称

第一行为物理单位，单位是一个七位的列表表示:

(length, time, mass, temperature, electric current, amount of light, amount of matter)
(长度、时间、质量、温度、电流、光量、物质量)

例如：[1, 0, 0] 表示长度， [1, -1, 0]表示（长度/时间）= 速度


参考用例：

    mlflow run PhySO -P data=mechanical.csv
