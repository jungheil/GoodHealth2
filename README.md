## GoodHealth2

<p align="center">
<img src="https://img.shields.io/badge/GoodHealth2-green.svg" title="GoodHealth2">
<img src="https://img.shields.io/badge/Author-Anonymous-red.svg" title="Author">
<a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" title="LICENSE"></a>
<a href="https://github.com/jungheil/GoodHealth2/actions/workflows/action.yml"><img src="https://github.com/jungheil/GoodHealth2/actions/workflows/action.yml/badge.svg?event=schedule" title="Health Report"></a>
</p>

大学生每日一用，确保健康。

### 部署GoodHealth2

1. Fork本仓库，或将该仓库上传到自己的github上。

2. 点击仓库的`Settings`，找到`Secrets`，点击`New repository secret`，新增如下几个值：

   | Name       | Value                                                    |
   | ---------- | -------------------------------------------------------- |
   | `USERNAME` | 您的学号                                                 |
   | `PASSWORD` | 您的一网通密码                                           |
   | `SENDKEY`  | 使用`pushplus`发送上报错误信息，见 https://www.pushplus.plus/ |

3. 将在早晨8点左右自动食用。想食用时间可自行修改`.github/workflows/action.yml`文件，注意使用 UTC 时间。

4. 支持多账号上报，`Secrets`中用户之间使用`,`隔开，`config`文件中使用`---`隔开，账户数量以`config`文件为准

### 说明

1. 食用时间并不准确，可能会有延迟（甚至长达几个小时）。可自行使用服务器或云函数解决。
1. 点击仓库的`Actions`可查看程序运行状况。
1. 程序运行失败时 github action 会自动发送邮件到您邮箱当中。
2. 本工具仅限身体健康者食用，否则后果自负。

### 致谢

本项目上报上报方案参考项目[jksb-sysu](https://github.com/Coelophylla/jksb-sysu)。