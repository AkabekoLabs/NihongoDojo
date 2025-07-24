"""
Colab環境用のユーティリティ関数
"""

import os
import torch
import subprocess
import shutil
import warnings


def check_gpu_environment():
    """GPU環境をチェックして情報を表示"""
    print("=== GPU環境チェック ===")
    print(f"CUDA利用可能: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"GPU名: {torch.cuda.get_device_name(0)}")
        print(f"GPUメモリ: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        print("✅ GPU環境が正常に検出されました！")
    else:
        print("❌ GPUが検出されません！")
        print("上記の手順でGPUを有効にしてください。")
        print("その後、ランタイムを再起動してこのセルを再実行してください。")
    
    # Colab環境かチェック
    if 'COLAB_GPU' in os.environ:
        print(f"\nGoogle Colab GPU: {os.environ['COLAB_GPU']}")
    elif 'COLAB_' in "".join(os.environ.keys()):
        print("\nGoogle Colab環境です。GPUを有効にしてください。")
    else:
        print("\nローカル環境で実行中")
    
    return torch.cuda.is_available()


def setup_japanese_font():
    """日本語フォントを設定"""
    import matplotlib.pyplot as plt
    import matplotlib
    
    try:
        import japanize_matplotlib
        # japanize_matplotlibが利用可能な場合、自動的に日本語フォントが設定される
        print("日本語フォントの設定が完了しました")
        return True
    except ImportError:
        print("Warning: japanize-matplotlib not found. Japanese text in plots may not display correctly.")
        print("Install with: pip install japanize-matplotlib")
        
        # フォールバック：利用可能な日本語フォントを探す
        import matplotlib.font_manager as fm
        
        # 利用可能な日本語フォントを検索
        japanese_fonts = [
            'IPAexGothic',
            'IPAGothic', 
            'Hiragino Sans',
            'Yu Gothic',
            'Meiryo',
            'Takao',
            'VL Gothic',
            'Noto Sans CJK JP'
        ]
        
        available_fonts = [font.name for font in fm.fontManager.ttflist]
        
        for font_name in japanese_fonts:
            if font_name in available_fonts:
                plt.rcParams['font.family'] = font_name
                print(f"フォールバック: {font_name}を使用します")
                return True
        
        print("日本語フォントが見つかりません。英語フォントを使用します。")
        return False
    
    # フォントキャッシュをクリア
    cache_dir = os.path.expanduser('~/.cache/matplotlib')
    if os.path.exists(cache_dir):
        try:
            shutil.rmtree(cache_dir)
        except:
            pass
    
    # フォントの警告を抑制
    warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')