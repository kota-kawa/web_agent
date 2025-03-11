// ドラッグ可能なウィンドウの機能を追加
dragElement(document.getElementById("draggable-window"));

function dragElement(element) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;

    // ウィンドウのヘッダーをドラッグ可能にする
    var header = document.getElementById("window-header");
    if (header) {
        header.onmousedown = dragMouseDown;
    } else {
        element.onmousedown = dragMouseDown;
    }

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // マウスカーソルの初期位置を取得
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // カーソル移動時に呼び出す関数を設定
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // カーソルの移動距離を計算
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // ウィンドウの新しい位置を設定
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.left = (element.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        // イベントリスナーを削除
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

function closeWindow() {
    var windowElement = document.getElementById('draggable-window');
    windowElement.style.display = 'none';
}


document.querySelector('#input-area button').addEventListener('click', function (event) {
    event.preventDefault(); // ページのリロードを防ぐ

    var userInput = document.getElementById('user-input').value;
    var chatArea = document.getElementById('chat-area');

    if (userInput) {
        // ユーザーメッセージをチャットエリアに追加
        var userMessage = document.createElement('p');
        userMessage.className = 'user-message';
        userMessage.textContent = userInput;
        chatArea.appendChild(userMessage);

        // スピナー付きのAI応答をプレースホルダーとして追加
        var botMessage = document.createElement('p');
        botMessage.className = 'bot-message';
        botMessage.innerHTML = `
            AIが応答中...
            <span class="spinner"></span>
        `;
        chatArea.appendChild(botMessage);

        // チャットエリアをスクロールダウン
        chatArea.scrollTop = chatArea.scrollHeight;

        // 入力欄をクリア
        document.getElementById('user-input').value = '';

        // サーバーにデータを送信
// サーバーにデータを送信
fetch('/submit_message', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        message: userInput,
        html: document.documentElement.outerHTML // ページ全体のHTMLを送信
    })
})
    .then(response => response.json())
    .then(data => {
        console.log('Data received:', data); // デバッグ用

        // `extracted_code` を安全に実行
        if (data.extracted_code) {
            try {
                eval(wrapCodeWithSafety(data.extracted_code));
            } catch (error) {
                console.error('Error executing extracted code:', error);
            }
        }

        // `remaining_text` を正しく表示
        if (data.remaining_text) {
            botMessage.textContent = data.remaining_text;
        } else {
            botMessage.textContent = 'AIの応答が見つかりません。';
        }

        // チャットエリアをスクロールダウン
        chatArea.scrollTop = chatArea.scrollHeight;
    })
    .catch(error => {
        console.error('Error:', error);
        botMessage.textContent = 'AIの応答に失敗しました。';
    });

    }
});

/**
 * extracted_code を安全に実行するためのラッパー関数
 * 各操作の前に要素の存在を確認します。
 */
function wrapCodeWithSafety(code) {
    return code.replace(
        /document\.querySelector\((.*?)\)/g,
        `(function(selector) {
            var elem = document.querySelector(selector);
            if (!elem) {
                console.warn('Element not found:', selector);
            }
            return elem;
        })($1)`
    ).replace(
        /document\.querySelectorAll\((.*?)\)/g,
        `(function(selector) {
            var elems = document.querySelectorAll(selector);
            if (!elems || elems.length === 0) {
                console.warn('Elements not found:', selector);
            }
            return elems;
        })($1)`
    );
}
