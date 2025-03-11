from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_core.runnables import RunnableSequence
from dotenv import load_dotenv
import os
import re

# Load the .env file
load_dotenv()

# Get environment variables
groq_api_key = os.getenv("GROQ_API_KEY")

def process_comment_text(comment_text):
    """Process the comment text"""
    return comment_text

def create_faiss_index(text):
    # Split text into overlapping chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,
    )
    # Split the text
    splited_text = text_splitter.split_text(text)
    
    # Return the split text (no embedding conversion)
    return splited_text

def escape_curly_braces(text):
    """Escape curly braces in the text."""
    return text.replace("{", "{{").replace("}", "}}")

def run_qa_chain(message, context):
    # Escape curly braces in the context
    escaped_context = escape_curly_braces(context)
    # Get Groq API key
    groq_chat = ChatGroq(groq_api_key=groq_api_key, model_name="llama3-70b-8192")

    # System prompt with context directly used
    system_prompt = escape_curly_braces(
        "あなたは渡されたHTMLコードとユーザーからの指示によってJavascriptコードを生成するアシスタントです"
        "Javascriptコードはeval()関数に入れてそのまま実行できる形で出力してほしい。eval関数はコードに含める必要はなない。"
        "関数の中にコードは生成せずに、呼び出さなくても実行できるようする。"
        "重要！！！ 1つの処理を実行するごとに、0.5秒待機する。 データの送信の処理はやってはいけない。！！！"
        "また、あなたは日本人なので、日本語で回答してください。必ず日本語で。"
        """



        例：
        document.querySelector('input[name="name"]').setAttribute('value', '自分の名前');
        document.querySelector('input[name="name"]').dispatchEvent(new Event('input')); // 入力イベントをトリガー
        document.querySelector('input[name="email"]').setAttribute('value', 'メールアドレス');
        document.querySelector('input[name="email"]').dispatchEvent(new Event('input'));
        document.querySelector('input[name="question1"][value="123"]').setAttribute('checked', true);
        document.querySelectorAll('input[name="question2[]"][value="答え２"], input[name="question2[]"][value="答え３"], input[name="question2[]"][value="答え５"]').forEach(checkbox => {
            checkbox.setAttribute('checked', true);
            checkbox.dispatchEvent(new Event('change')); // チェンジイベントをトリガー
        });
        document.querySelector('input[name="question3"]').setAttribute('value', '答え６');
        document.querySelector('input[name="question3"]').dispatchEvent(new Event('input'));


        // テキストエリアに値を入力
        document.querySelector('textarea[name="comments"]').value = 'コメントを入力します';
        document.querySelector('textarea[name="comments"]').dispatchEvent(new Event('input')); // 入力イベントをトリガー

        // ドロップダウン（セレクトボックス）で選択を変更
        document.querySelector('select[name="options"]').value = 'optionValue'; // 選択肢の値を指定
        document.querySelector('select[name="options"]').dispatchEvent(new Event('change')); // チェンジイベントをトリガー

        // ラジオボタンを選択
        document.querySelector('input[name="gender"][value="male"]').checked = true;
        document.querySelector('input[name="gender"][value="male"]').dispatchEvent(new Event('change')); // チェンジイベントをトリガー

        // ボタンをクリック
        document.querySelector('button[name="submit"]').click(); // クリック操作

        // チェックボックスの選択を解除
        document.querySelectorAll('input[name="agree_terms"]').forEach(checkbox => {
            checkbox.checked = false;
            checkbox.dispatchEvent(new Event('change')); // チェンジイベントをトリガー
        });

        """
        "プロフィール情報 名前:こうた メールアドレス:kouta@gmail.com メッセージ:おはよう！"
        "\n\n"
        f"{escaped_context}"  # Use escaped context directly in the prompt
    )

    # Create prompt template with system and human messages
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    # Create the chain without retriever, only input
    rag_chain = (
        {"input": RunnablePassthrough()}  # Only pass user input (message)
        | prompt
        | groq_chat
        | StrOutputParser()
    )

    # Get response
    response = rag_chain.invoke(message)

    return response


def chain_main(message, html_code):
    comment_text = str(html_code)

    # Process comment text
    text = process_comment_text(comment_text)

    # Directly run the QA chain with text
    output = run_qa_chain(message, text)

    # 正規表現を使ってjavascriptコード部分を抽出
    code_match = re.search(r'```(.*?)```', output, re.DOTALL)
    if code_match:
        extracted_code = code_match.group(1).strip()
        
        # "javascript"文字列を削除
        if extracted_code.startswith("javascript"):
            extracted_code = extracted_code[len("javascript"):].strip()
        
        print("抽出されたコード:")
        print(extracted_code)
        
        # 残りのテキストを表示
        remaining_text = re.sub(r'```(.*?)```', '', output, flags=re.DOTALL).strip()
        print("残りのテキスト:")
        print(remaining_text)
        return extracted_code, remaining_text
    
    else:
        print("Javascriptコードが見つかりませんでした。")

