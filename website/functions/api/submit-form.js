export async function onRequestPost(context) {
  try {
    console.log('[Debug] 开始处理表单提交');
    const data = await context.request.json();
    console.log('[Debug] 收到的表单数据:', JSON.stringify(data));

    // 发送到飞书群
    console.log('[Debug] 正在发送到飞书群...');
    const botResponse = await fetch('https://open.feishu.cn/open-apis/bot/v2/hook/4e72b69a-2c95-49c9-bbf3-63a39e2e0cc7', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "msg_type": "text",
        "content": {
          "text": `
新的软件下载申请

姓名: ${data.name}
邮箱: ${data.email}
手机: ${data.phone}
使用目的: ${data.purpose}
          `
        }
      })
    });

    // 记录原始响应
    const botResponseText = await botResponse.text();
    console.log('[Debug] 机器人发送原始响应:', botResponseText);

    let botResult;
    try {
      botResult = JSON.parse(botResponseText);
    } catch (parseError) {
      console.error('[Error] 解析响应失败:', parseError);
      throw new Error(`响应解析失败: ${botResponseText}`);
    }

    console.log('[Debug] 机器人发送响应(解析后):', JSON.stringify(botResult));

    if (botResult.code !== 0) {
      throw new Error('发送消息失败: ' + JSON.stringify(botResult));
    }

    return new Response(JSON.stringify({
      success: true,
      debug: {
        messageSent: true,
        botResponse: botResult
      }
    }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    console.error('[Error]', error);
    return new Response(JSON.stringify({ 
      success: false, 
      error: error.message,
      stack: error.stack 
    }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
