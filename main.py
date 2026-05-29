"""银渐层沉思录 - 公众号智能体入口"""
import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def save_output(state: dict):
    """保存生成结果到本地文件"""
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    # 保存HTML
    html_path = out_dir / "article.html"
    html_path.write_text(state.get("html_content", ""), encoding="utf-8")

    # 保存Markdown原文
    md_path = out_dir / "article.md"
    md_content = f"# {state.get('article_title', '')}\n\n{state.get('article_content', '')}"
    md_path.write_text(md_content, encoding="utf-8")

    # 保存元信息
    meta = {
        "title": state.get("article_title"),
        "digest": state.get("article_digest"),
        "topic": state.get("topic"),
        "angle": state.get("topic_angle"),
        "status": state.get("status"),
        "publish_job_id": state.get("publish_job_id"),
    }
    meta_path = out_dir / "meta.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n📁 输出文件已保存到 output/ 目录：")
    print(f"   - output/article.html  （微信排版HTML，可在浏览器预览）")
    print(f"   - output/article.md    （原始Markdown）")
    print(f"   - output/meta.json     （元信息）")


def main():
    parser = argparse.ArgumentParser(description="银渐层沉思录 - 公众号智能体")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="只生成内容，不发布到公众号",
    )
    parser.add_argument(
        "--used-topics",
        nargs="*",
        default=[],
        help="已使用过的选题列表（避免重复）",
    )
    args = parser.parse_args()

    # dry-run模式
    if args.dry_run:
        os.environ["DRY_RUN"] = "true"
        print("🔧 DRY_RUN 模式：只生成内容，不发布")
    else:
        dry_run_env = os.getenv("DRY_RUN", "true").lower()
        if dry_run_env == "true":
            print("🔧 DRY_RUN 模式（来自.env）：只生成内容，不发布")

    # 检查必要的API Key
    missing = []
    if not os.getenv("DEEPSEEK_API_KEY"):
        missing.append("DEEPSEEK_API_KEY")
    if not os.getenv("TAVILY_API_KEY"):
        missing.append("TAVILY_API_KEY")
    if missing:
        print(f"❌ 缺少必要的API Key: {', '.join(missing)}")
        print("   请复制 .env 为 .env 并填写对应的Key")
        sys.exit(1)

    print("\n" + "="*50)
    print("  银渐层沉思录 · 公众号智能体")
    print("="*50 + "\n")

    from graph import agent

    initial_state = {
        "used_topics": args.used_topics,
        "format_retry_count": 0,
    }

    try:
        final_state = agent.invoke(initial_state)
        save_output(final_state)

        print("\n" + "="*50)
        status = final_state.get("status", "unknown")
        if status in ("published", "dry_run_complete"):
            print(f"🎉 完成！文章「{final_state.get('article_title')}」")
            if status == "published":
                print(f"   已发布到公众号，publish_id: {final_state.get('publish_job_id')}")
            else:
                print("   已生成到 output/ 目录，请检查后手动发布")
        else:
            print(f"⚠️  流程结束，状态: {status}")
            if final_state.get("error"):
                print(f"   错误: {final_state['error']}")
        print("="*50)

    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 运行出错: {e}")
        raise


if __name__ == "__main__":
    main()
