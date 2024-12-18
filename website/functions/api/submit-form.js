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

    return new Response(JSON.stringify({
      success: true,
      debug: {
        hasToken: !!tokenData.tenant_access_token,
        tokenResponse: tokenData
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
