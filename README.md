# wireless-testing-platform
端到端无线测试平台

#安装：
1. 安装python
2. 安装MySQLdb
3. 安装Torando及其依赖包
4. 安装lazyxml python模块
5. 安装threadpool python模块

#执行
python Main.py

#访问
http://localhost

#更新
1. 兼容windows开发环境*
2. 添加用例集功能
3. 添加重跑功能
4. 修复多线程bug *
5. 优化程序安装/卸载逻辑 *
6. 优化prepare逻辑 *
7. 支持设备执行指定用例次数后重启 *
8. UI界面优化 *
9. 代码异常处理
10. 支持测试结果日志分析*
11. mysql断链修复*

# API访问
## 测试执行
http://localhost/process?apkpath=lingxi_v3.1.2005.autotest_signed.apk&projectname=&rel=json

## 设备列表：
xml格式：http://localhost/devices?rel=xml&pretty=false
json格式：http://localhost/devices?rel=json&pretty=false

## 结果集访问
http://localhost/resultList?uuid=-8e605ad7-eff2-4584-b9aa-5cf16a91f359

## 单用例结果访问
http://localhost/result?name=test5_BVT_1013