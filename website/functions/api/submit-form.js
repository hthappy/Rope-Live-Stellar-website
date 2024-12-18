export async function onRequestPost(context) {
  try {
    const data = await context.request.json();
    
    // 飞书应用凭证
    const FEISHU_APP_ID = context.env.FEISHU_APP_ID;
    const FEISHU_APP_SECRET = context.env.FEISHU_APP_SECRET;
    
    // 获取飞书访问令牌
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
    const accessToken = tokenData.tenant_access_token;

    // 发送邮件
    await fetch('https://open.feishu.cn/open-apis/mail/v1/messages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
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
        },
        "email_info": {
          "subject": "测试",
          "from_user": "service@ai-yy.com",
          "to_users": ["service@ai-yy.com"]
        }
      })
    });

    return new Response(JSON.stringify({ success: true }), {
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (error) {
    return new Response(JSON.stringify({ success: false, error: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
