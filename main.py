"""
个人科研助手主程序
支持命令行和Web两种模式
"""
import argparse
import sys
from pathlib import Path
from app.core.research_assistant import ResearchAssistant
from app.api.routes import create_app


def cli_mode(assistant: ResearchAssistant):
    """命令行交互模式"""
    print("\n" + "="*60)
    print("🔬 个人科研助手 - 命令行模式")
    print("="*60)
    print("\n可用命令：")
    print("  ask <问题>        - 询问文档相关问题")
    print("  similarity        - 分析文档相似性")
    print("  recommend         - 获取研究推荐")
    print("  web <URL>         - 抓取并总结网页内容")
    print("  list              - 列出所有文档")
    print("  list-web          - 列出已抓取的网页")
    print("  help              - 显示帮助")
    print("  quit/exit         - 退出程序")
    print("\n" + "-"*60 + "\n")
    
    while True:
        try:
            user_input = input("科研助手> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("再见！")
                break
            
            if user_input.lower() == 'help':
                print("\n可用命令：")
                print("  ask <问题>        - 询问文档相关问题")
                print("  similarity        - 分析文档相似性")
                print("  recommend         - 获取研究推荐")
                print("  web <URL>         - 抓取并总结网页内容")
                print("  list              - 列出所有文档")
                print("  list-web          - 列出已抓取的网页")
                print("  quit/exit         - 退出程序\n")
                continue
            
            if user_input.lower() == 'list':
                docs = assistant.get_document_list()
                if docs:
                    print("\n已加载的文档：")
                    for i, doc in enumerate(docs, 1):
                        print(f"  {i}. {doc}")
                else:
                    print("\n暂无文档")
                print()
                continue
            
            if user_input.lower() == 'list-web':
                web_contents = assistant.get_web_contents_list()
                if web_contents:
                    print("\n已抓取的网页：")
                    for i, content in enumerate(web_contents, 1):
                        print(f"  {i}. {content}")
                else:
                    print("\n暂无网页内容")
                print()
                continue
            
            if user_input.lower().startswith('web '):
                url = user_input[4:].strip()
                if url:
                    print(f"\n正在抓取并总结网页: {url}")
                    summary = assistant.summarize_web_content(url)
                    print("\n总结结果：")
                    print("-" * 60)
                    print(summary)
                    print("-" * 60 + "\n")
                else:
                    print("请输入URL")
                continue
            
            if user_input.lower() == 'similarity':
                print("\n正在分析文档相似性...")
                result = assistant.analyze_similarity()
                print("\n分析结果：")
                print("-" * 60)
                print(result)
                print("-" * 60 + "\n")
                continue
            
            if user_input.lower() == 'recommend':
                print("\n正在生成研究推荐...")
                result = assistant.recommend_research()
                print("\n推荐结果：")
                print("-" * 60)
                print(result)
                print("-" * 60 + "\n")
                continue
            
            if user_input.lower().startswith('ask '):
                question = user_input[4:].strip()
                if question:
                    print("\n正在思考...")
                    answer = assistant.ask(question)
                    print("\n回答：")
                    print("-" * 60)
                    print(answer)
                    print("-" * 60 + "\n")
                else:
                    print("请输入问题")
                continue
            
            # 默认作为问题处理
            print("\n正在思考...")
            answer = assistant.ask(user_input)
            print("\n回答：")
            print("-" * 60)
            print(answer)
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"\n错误: {e}\n")


def web_mode(assistant: ResearchAssistant):
    """Web界面模式"""
    app = create_app(assistant)
    
    @app.route('/')
    def index():
        from flask import send_from_directory
        return send_from_directory('app/web/templates', 'index.html')
    
    print("\n" + "="*60)
    print("🔬 个人科研助手 - Web模式")
    print("="*60)
    print("\n服务器启动中...")
    print("访问地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务器\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='个人科研助手')
    parser.add_argument('--mode', choices=['cli', 'web'], default='cli',
                       help='运行模式: cli (命令行) 或 web (网页)')
    parser.add_argument('--documents-dir', default='documents',
                       help='PDF文档目录 (默认: documents)')
    parser.add_argument('--rebuild-index', action='store_true',
                       help='重建向量索引')
    parser.add_argument('--no-quantization', action='store_true',
                       help='禁用模型量化（需要更多显存）')
    
    args = parser.parse_args()
    
    # 检查文档目录
    documents_dir = Path(args.documents_dir)
    if not documents_dir.exists():
        documents_dir.mkdir(parents=True)
        print(f"创建文档目录: {documents_dir}")
        print(f"请将PDF文件放入 {documents_dir} 目录")
    
    # 初始化助手
    print("初始化科研助手...")
    assistant = ResearchAssistant(
        documents_dir=str(documents_dir),
        use_quantization=not args.no_quantization
    )
    
    # 初始化（处理文档和构建索引）
    assistant.initialize(rebuild_index=args.rebuild_index)
    
    # 运行对应模式
    if args.mode == 'web':
        web_mode(assistant)
    else:
        cli_mode(assistant)


if __name__ == '__main__':
    main()

