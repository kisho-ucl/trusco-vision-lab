# Docs Index

このディレクトリは、研究の「後から読める知識」と「作業中のメモ」を分けて管理する。

新しく参加した人や、少し時間を置いた自分が読む場合は、まず `DASHBOARD.md` とこのindexから入る。

## Start Here

- [Research Dashboard](../DASHBOARD.md): 現在地、仮説、次の判断。
- [Development Guide](dev/DEVELOPMENT_GUIDE.md): AIと進める軽量な仕様駆動開発の手順。
- [Roadmap](project/roadmap.md): M2春から10月頃までの進め方。
- [Vision Context](project/vision_context.md): TRUSCO映像処理基盤とdigital twin構想の背景。
- [Survey README](../survey/README.md): 関連研究調査の入口。
- [Logs](../logs/README.md): 日々の判断、議論、報告会フィードバック。

## project/ — 修論・研究方針

他の人が読んでも研究の全体像が分かるレベルに育てたい文書。

- [project/research_plan.md](project/research_plan.md): 修論全体の研究計画。
- [project/roadmap.md](project/roadmap.md): 研究フェーズとdeliverable。
- [project/vision_context.md](project/vision_context.md): TRUSCOの映像処理基盤、tracking、digital twinとの接続。
- [project/vision_thesis_options.md](project/vision_thesis_options.md): Visionを修論にどう入れるかの選択肢整理。

## dev/ — 実装・ツール

- [dev/DEVELOPMENT_GUIDE.md](dev/DEVELOPMENT_GUIDE.md): Spec / Mini Spec / Visual Draft / Implementationの進め方。
- [dev/trusco_dataset_spec.md](dev/trusco_dataset_spec.md): トラッキングJSON・動画・ts_cacheのデータ仕様。
- [dev/hands_on_investigation_plan.md](dev/hands_on_investigation_plan.md): 実装・データ確認に入るための調査計画。
- [dev/implementation_backlog.md](dev/implementation_backlog.md): baseline、tool、module候補の置き場。
- [dev/experiment_log.md](dev/experiment_log.md): 実験ログの初期置き場。
- [dev/specs/semi_auto_annotation/SPEC.md](dev/specs/semi_auto_annotation/SPEC.md): 半自動annotation workflowの親仕様。
- [dev/specs/semi_auto_annotation/MINI_SPECS.md](dev/specs/semi_auto_annotation/MINI_SPECS.md): 半自動annotation workflowの実装単位。
- [dev/specs/semi_auto_annotation/VISUAL_DRAFT_v0_5.md](dev/specs/semi_auto_annotation/VISUAL_DRAFT_v0_5.md): annotation tool v0.5のVisual Draft。

## tools/ — 実装済みツール

実装済みのツールはそれぞれREADMEを持つ。

- [tools/annotation/README.md](../tools/annotation/README.md): annotation tool v0（Flask + browser UI）。clip単位でフレームをめくりながら作業区間を付けるWebツール。**完成・運用可能。**
- [tools/dataset_generation/README.md](../tools/dataset_generation/README.md): extract_clips.py。tracking JSONからtrack_id単位の人物cropクリップを生成。
- [tools/tracking_viewer/README.md](../tools/tracking_viewer/README.md): export_overlay.py。stitch動画にtracking結果をオーバーレイしてmp4に書き出す。

## archive/ — 退避済み

- [archive/progress_report_2026-05.md](archive/progress_report_2026-05.md): 5月報告に向けた進捗整理。
- [archive/progress_report_esa_2026-05-21.md](archive/progress_report_esa_2026-05-21.md): esa貼り付け用の報告会メモ。
- [archive/semi_auto_annotation_plan.md](archive/semi_auto_annotation_plan.md): specs/に移行済みの旧プラン。

## Future Maintained Assets

今後、後輩や共同研究者に共有できるレベルまで育てたいもの。

- TRUSCO映像処理基盤のSkill / module documentation
- annotation schemaの確定（認識モデルから逆算・Design Day待ち）
- feature extraction / clustering / dataset export の手順
- baseline実験の再現手順
