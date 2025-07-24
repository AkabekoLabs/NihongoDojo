# Nihongo DoJo 🥋

日本語学習AI用のGRPOデータセット生成フレームワーク

## 🎯 概要

Nihongo DoJoは、日本語AIモデルの強化学習（GRPO）用データセットを生成するツールです。

## 🚀 クイックスタート

### インストール
```bash
git clone https://github.com/akabekolabs/nihongo-dojo.git
cd nihongo-dojo
pip install -r requirements.txt
```

### 基本的な使い方
```bash
# 小規模データセット（1万タスク）を生成
python generate_datasets.py --preset small

# 中規模データセット（5万タスク）を生成
python generate_datasets.py --preset medium

# 特定の学年の漢字タスクを生成
python generate_datasets.py --grades 1 2 3 --tasks KANJI_READING KANJI_WRITING
```

## 📋 タスク一覧

### 基本タスク（6種類）
- `KANJI_READING` - 漢字の読み方
- `KANJI_WRITING` - ひらがな→漢字変換
- `PARTICLE_FILL` - 助詞の穴埋め
- `KEIGO_CONVERSION` - 敬語変換
- `WORD_ORDER` - 語順並び替え
- `COUNTER_WORD` - 助数詞選択


## Notebook
- <a href="https://colab.research.google.com/github/AkabekoLabs/nihongo-dojo/blob/main/notebooks/training_kanji.ipynb"　target="_blank">>漢字トレーニング</a>

## 🎖️ 学習サポート機能

### タスク特化型報酬関数
```python
from nihongo_dojo.reward import (
    ParticleFillRewardFunctions,  # 助詞用
    WordOrderRewardFunctions,     # 語順用
    KanjiRewardFunctions,         # 漢字用（部首類似性評価）
    CounterRewardFunctions,       # 助数詞用（カテゴリー評価）
    KeigoRewardFunctions          # 敬語用（丁寧語対応）
)
```

### 学習ログと可視化
```python
from nihongo_dojo.colab import TrainingLogger, GRPOVisualizationCallback

# ログ管理（タスク名付き）
logger = TrainingLogger(log_dir="./logs", task_name="kanji")

# リアルタイム可視化
visualization_callback = GRPOVisualizationCallback(
    update_frequency=5,
    log_filename=logger.log_filename
)
```

## 📚 学習ノートブック

Google Colab用のサンプルノートブックを提供：

- `notebooks/training_*_balanced.ipynb` - 各タスク用の最適化済みノートブック
- 推奨環境: Google Colab T4 GPU
- 使用モデル: Qwen3-4B


### カスタム生成例
```bash
# ビジネス日本語特化
python generate_datasets.py \
    --tasks BUSINESS_JAPANESE KEIGO_CONVERSION \
    --custom-size 30000

# 初級者向け漢字学習
python generate_datasets.py \
    --grades 1 2 3 \
    --tasks KANJI_READING KANJI_WRITING \
    --custom-size 20000
```

### HuggingFaceへのアップロード
```bash
python upload_to_huggingface.py \
    --input-path ./datasets/nihongo-dojo-medium \
    --dataset-name my-nihongo-dataset
```

## 🔧 必要環境
- Python 3.8以上
- 8GB以上のRAM
- 10GB以上のディスク容量

## 📜 ライセンス
Apache 2.0 License

## 🙏 謝辞
日本語教育とAI研究の発展に貢献することを目指しています。