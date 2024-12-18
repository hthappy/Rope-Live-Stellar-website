export async function onRequestPost(context) {
  const corsHeaders = {
    'Access-Control-Allow-Origin': context.request.headers.get('Origin'),
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin'
  };

  try {
    // 获取访问者IP
    const clientIP = context.request.headers.get('CF-Connecting-IP') || 
                    context.request.headers.get('X-Real-IP') || 
                    'unknown';
    
    console.log('[Debug] 访问者IP:', clientIP);

    // 检查IP是否在24小时内提交过
    const submitRecord = await context.env.SUBMIT_RECORDS.get(`ip_${clientIP}`);
    if (submitRecord) {
      const lastSubmitTime = new Date(submitRecord);
      const now = new Date();
      const hoursDiff = (now - lastSubmitTime) / (1000 * 60 * 60);
      
      if (hoursDiff < 24) {
        return new Response(JSON.stringify({
          success: false,
          error: '24小时内只能提交一次申请'
        }), {
          status: 429,
          headers: {
            'Content-Type': 'application/json',
            ...corsHeaders
          }
        });
      }
    }

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
Rope-Live 体验申请

姓名: ${data.name}
邮箱: ${data.email}
QQ: ${data.qq}
使用目的: ${data.purpose}
IP: ${clientIP}
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

    // 记录IP提交时间
    await context.env.SUBMIT_RECORDS.put(`ip_${clientIP}`, new Date().toISOString(), {
      expirationTtl: 86400  // 24小时后自动过期
    });

    return new Response(JSON.stringify({
      success: true,
      debug: {
        messageSent: true,
        botResponse: botResult
      }
    }), {
      headers: { 
        'Content-Type': 'application/json',
        ...corsHeaders 
      }
    });
  } catch (error) {
    console.error('[Error]', error);
    return new Response(JSON.stringify({ 
      success: false, 
      error: error.message,
      stack: error.stack 
    }), {
      status: 500,
      headers: { 
        'Content-Type': 'application/json',
        ...corsHeaders 
      }
    });
  }
}

export async function onRequestOptions(context) {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': context.request.headers.get('Origin'),
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Vary': 'Origin'
    }
  });
}
