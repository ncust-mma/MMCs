# INSTALLATION

## 1. 下载项目

有多种方式可以提供下载。

最简单的当然使用 `git` 命令，如下：

```bash
$ git clone https://github.com/Zeroto521/MMCs.git
```

这种方式可以下载到项目的最新版本，一般最新版中可能存在某些未知的 **bugs**。

也可以下载 release 发行版本，发行版本一般较为稳定。

发行版本下载页面如下：

https://github.com/Zeroto521/MMCs/releases

## 2. 安装环境

安装环境同样也有多种方式，但推荐使用 `pipenv` 工具安装。

同样不排除使用其他方式进行安装所需环境。

所需要的第三方库列表在[这可以找到](../requirements.txt)。

## 3. 配置

项目中部分内容涉及到隐私信息，因此部分配置采用文件导入配置。

在项目根目录中建立 `.env` 文件，需要配置的内容如下：

```
FLASK_ENV=production
FLASK_CONFIG=production
SENDGRID_API_KEY=xx
MAIL_USERNAME=noreply@domain.com
ADMIN_EMAIL=reciver@domain.com
```

### SENDGRID_API_KEY

因为事务邮件功能使用的是 sendgrid web api 所以需要相应密钥。

### MAIL_USERNAME

事务邮件默认发件人

### ADMIN_EMAIL

网站维护人员

## 4. 启动环境

```bash
$ cd MMCs
$ pipenv install --dev
$ pipenv shell
$ flask forge
$ flask translate compile
```

### 5. 运行

若是开发环境(**development**)，可以直接通过 `flask run` 命令运行。

若是生产环境(**production**)，则需要一些更复杂点的配置步骤。
