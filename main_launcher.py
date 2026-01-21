import sys
import os
import subprocess
import time
import webbrowser

def main():
    print("Initializing Project Health Dashboard...")
    
    # 1. 获取当前脚本所在的目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 定位 app.py 的路径
    app_path = os.path.join(base_dir, "app.py")
    
    # 3. 检查 app.py 是否存在
    if not os.path.exists(app_path):
        print(f"Error: Cannot find app.py at {app_path}")
        input("Press Enter to exit...")
        return

    # 4. 构造启动命令: streamlit run app.py
    # 使用 sys.executable 确保用的是当前的 python 解释器 (虚拟环境里的那个)
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    
    print("Starting local server...")
    
    # 5. 使用 subprocess 启动后台进程
    try:
        # Popen 不会阻塞，它会在后台跑
        process = subprocess.Popen(cmd)
        
        # 6. 等待几秒让服务启动
        time.sleep(3)
        
        # 7. 尝试自动打开浏览器 (Streamlit 其实通常会自动打开，但这行是双保险)
        # webbrowser.open("http://localhost:8501")
        
        print("Server is running! Please check your browser.")
        print("   (Close this window to stop the app)")
        
        # 8. 阻塞主进程，直到用户关闭窗口
        process.wait()
        
    except KeyboardInterrupt:
        print("\nStopping server...")
        process.terminate()
    except Exception as e:
        print(f"\nError occurred: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()