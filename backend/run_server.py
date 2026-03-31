#!/usr/bin/env python3
"""简单的后端启动脚本"""
import uvicorn
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 50)
    print("  启动后端服务...")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=9191,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动错误: {e}")
        import traceback
        traceback.print_exc()
