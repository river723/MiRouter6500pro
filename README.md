# Mi 6500pro Router Device Tracker

这是一个 Home Assistant 插件，用于追踪小米路由器 6500pro 所无线连接的设备。

## 安装

### 方法一：通过 HACS 安装

1. 打开 Home Assistant 的 HACS 页面。
2. 点击右上角的菜单按钮，选择 "自定义存储库"。
3. 在 URL 输入框中输入 `https://github.com/river723/MiRouter6500pro`，并选择类别为 "Integration"。
4. 点击 "添加" 按钮。
5. 在 HACS 的 "集成" 页面中搜索 `Mi 6500pro router` 并安装。

### 方法二：手动安装

1. 下载并解压插件代码到 Home Assistant 配置目录下的 `custom_components/mi6500pro` 目录。
2. 确保目录结构如下：
    ```
    ├── custom_components/
    │   └── mi6500pro/
    │       ├── __init__.py
    │       ├── manifest.json
    │       ├── device_tracker.py
    │       ├── encrypt.py
    │       └── const.py
    ```

   #### 配置

    1. 在 Home Assistant 配置文件 `configuration.yaml` 中添加以下内容：

    ```yaml
    device_tracker:
      - platform: mi6500pro
        host: YOUR_ROUTER_IP
        password: YOUR_ROUTER_PASSWORD
        scan_interval: 60
    ```

2. 重新启动 Home Assistant。

## 使用

插件安装完成后，您可以在 Home Assistant 中 "设置 - 设备与服务 - 实体" 中查看小米 6500pro 路由器所连接的无线设备。

## 贡献

欢迎提交问题和贡献代码！请访问 [GitHub 仓库](https://github.com/river723/MiRouter6500pro) 获取更多信息。

## 许可证


MIT License
