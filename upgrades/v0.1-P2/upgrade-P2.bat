@echo off
@title copy sth to current filepath

SET folderFlag=webUI.py
SET versionFlag=py39\Lib\site-packages\xformers-0.0.24.dist-info

echo 正在尝试更新...

if exist %folderFlag% (
    if exist %versionFlag% (
		rmdir /s /q py39\Lib\site-packages\xformer
		rmdir /s /q py39\Lib\site-packages\xformer-1.0.1.dist-info
		rmdir /s /q py39\Lib\site-packages\xformers
		rmdir /s /q py39\Lib\site-packages\xformers-0.0.23.post1.dist-info
		rmdir /s /q py39\Lib\site-packages\xformers-0.0.24.dist-info
		
    ) else (
        echo 更新失败
		echo 可能的原因
		echo 1已经更新过了
		echo 2文件编码有问题
		echo 请尝试跟随视频进行手动更新
    )
) else (
    echo 验证失败（无法定位webUI.py）
	echo 可能的原因
	echo 1没有和webUI.py放在同级目录下
	echo 2原包的webUI.py被改名了
	echo 请检查后重试或前往space.bilibili.com/1740338174以获取更多信息
)

echo end
PAUSE
