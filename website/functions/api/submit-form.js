export async function onRequestPost(context) {
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
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

    // 检查请求数据
    let data;
    try {
      data = await context.request.json();
      console.log('[Debug] 收到的表单数据:', JSON.stringify(data));
    } catch (parseError) {
      console.error('[Error] 解析请求数据失败:', parseError);
      return new Response(JSON.stringify({
        success: false,
        error: '无效的请求数据'
      }), {
        status: 400,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }

    // 验证必要字段
    if (!data.name || !data.email || !data.qq || !data.purpose) {
      return new Response(JSON.stringify({
        success: false,
        error: '请填写所有必要信息'
      }), {
        status: 400,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }

    // 发送到飞书群
    const botResponse = await fetch('https://open.feishu.cn/open-apis/bot/v2/hook/4e72b69a-2c95-49c9-bbf3-63a39e2e0cc7', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "msg_type": "text",
        "content": {
          "text": `
Rope-Live Stellar 体验申请

姓名: ${data.name}
邮箱: ${data.email}
QQ: ${data.qq}
行业：${data.industry}
公司/个人：${data.company || '无'}
公司规模: ${data.scale || '无'}
使用目的: ${data.purpose}
IP: ${clientIP}
          `
        }
      })
    });

    const botResponseText = await botResponse.text();
    let botResult;
    try {
      botResult = JSON.parse(botResponseText);
    } catch (parseError) {
      console.error('[Error] 解析飞书响应失败:', parseError);
      throw new Error('服务器处理失败');
    }

    if (botResult.code !== 0) {
      throw new Error('消息发送失败');
    }

    // 记录IP提交时间
    await context.env.SUBMIT_RECORDS.put(`ip_${clientIP}`, new Date().toISOString(), {
      expirationTtl: 600  // 24小时后自动过期
    });

    return new Response(JSON.stringify({
      success: true
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
      error: error.message || '服务器处理失败'
    }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        ...corsHeaders
      }
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
    }
  });
}