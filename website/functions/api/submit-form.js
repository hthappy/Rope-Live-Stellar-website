export async function onRequestPost(context) {
  try {
    console.log('[Debug] 开始处理表单提交');
    const data = await context.request.json();
    console.log('[Debug] 收到的表单数据:', JSON.stringify(data));
    
    // 检查环境变量
    const FEISHU_APP_ID = context.env.FEISHU_APP_ID;
    const FEISHU_APP_SECRET = context.env.FEISHU_APP_SECRET;
    
    console.log('[Debug] 环境变量检查:', {
      hasAppId: !!FEISHU_APP_ID,
      hasAppSecret: !!FEISHU_APP_SECRET
    });
    
    // 获取飞书访问令牌
    console.log('[Debug] 正在获取飞书访问令牌...');
    const tokenResponse = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET
      })
    });
    
    const tokenData = await tokenResponse.json();
    console.log('[Debug] 访问令牌响应:', JSON.stringify(tokenData));
    
    if (!tokenData.tenant_access_token) {
      throw new Error('获取访问令牌失败: ' + JSON.stringify(tokenData));
    }

    // 发送邮件
    console.log('[Debug] 正在发送邮件...');
    const emailResponse = await fetch('https://open.feishu.cn/open-apis/mail/v1/mailboxes/service@ai-yy.com/messages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${tokenData.tenant_access_token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        "subject": "新的软件下载申请",
        "content": `
新的软件下载申请

姓名: ${data.name}
邮箱: ${data.email}
手机: ${data.phone}
使用目的: ${data.purpose}
        `,
        "to": ["service@ai-yy.com"]
      })
    });

    // 记录原始响应
    const emailResponseText = await emailResponse.text();
    console.log('[Debug] 邮件发送原始响应:', emailResponseText);

    let emailResult;
    try {
      emailResult = JSON.parse(emailResponseText);
    } catch (parseError) {
      console.error('[Error] 解析邮件响应失败:', parseError);
      throw new Error(`邮件响应解析失败: ${emailResponseText}`);
    }

    console.log('[Debug] 邮件发送响应(解析后):', JSON.stringify(emailResult));

    if (!emailResult.code || emailResult.code !== 0) {
      throw new Error('发送邮件失败: ' + JSON.stringify(emailResult));
    }

    return new Response(JSON.stringify({
      success: true,
      debug: {
        hasToken: true,
        emailSent: true,
        emailResponse: emailResult
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
