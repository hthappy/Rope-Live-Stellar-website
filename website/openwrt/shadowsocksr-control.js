/**
 * ShadowSocksR 菜单动态控制脚本
 * 根据 URL 参数动态显示/隐藏 ShadowSocksR 菜单项
 */

(function() {
    'use strict';
    
    // 检查 URL 参数
    function checkShowSSRParameter() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.has('show_ssr') && urlParams.get('show_ssr') === '1';
    }
    
    // 添加或移除 CSS 类
    function toggleSSRVisibility() {
        const body = document.body;
        
        if (checkShowSSRParameter()) {
            body.classList.add('show-ssr');
            console.log('ShadowSocksR menu enabled via URL parameter');
        } else {
            body.classList.remove('show-ssr');
            console.log('ShadowSocksR menu hidden (no show_ssr parameter)');
        }
    }
    
    // 直接隐藏 ShadowSocksR 菜单项（只隐藏 ShadowSocksR，保留其他服务）
    function hideSSRMenuItems() {
        if (checkShowSSRParameter()) {
            return; // 如果有参数，不隐藏
        }
        
        // 只在菜单页面隐藏菜单项，不影响具体功能页面的显示
        if (window.location.pathname.includes('/admin/services/shadowsocksr')) {
            return; // 如果当前就在 ShadowSocksR 页面，不隐藏任何内容
        }
        
        // 查找并隐藏 ShadowSocksR 相关的菜单项
        const selectors = [
            'a[data-title*="ShadowSocksR"]',
            'a[data-title*="shadowsocksr"]',
            'a[href*="/admin/services/shadowsocksr"]'
        ];
        
        selectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    // 只隐藏 ShadowSocksR 相关的链接
                    const href = element.getAttribute('href') || '';
                    const title = element.getAttribute('data-title') || '';
                    const text = element.textContent || element.innerText || '';
                    
                    // 确保只隐藏 ShadowSocksR 相关的项目
                    if (href.includes('shadowsocksr') || 
                        title.toLowerCase().includes('shadowsocksr') ||
                        text.includes('ShadowSocksR')) {
                        
                        element.style.display = 'none';
                        
                        // 隐藏父级 li 元素，但要确保不影响其他服务
                        const parentLi = element.closest('li');
                        if (parentLi) {
                            // 检查父级 li 是否只包含 ShadowSocksR 相关内容
                            const otherLinks = parentLi.querySelectorAll('a:not([href*="shadowsocksr"]):not([data-title*="shadowsocksr"])');
                            if (otherLinks.length === 0) {
                                parentLi.style.display = 'none';
                            }
                        }
                    }
                });
            } catch (e) {
                console.warn('Selector not supported:', selector);
            }
        });
    }
    
    // 监听 DOM 变化，处理动态加载的菜单
    function observeMenuChanges() {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // 延迟执行，确保菜单完全加载
                    setTimeout(hideSSRMenuItems, 100);
                }
            });
        });
        
        // 观察主菜单容器
        const mainMenu = document.querySelector('#mainmenu');
        if (mainMenu) {
            observer.observe(mainMenu, {
                childList: true,
                subtree: true
            });
        }
        
        // 观察整个 body，以防菜单在其他地方
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // 初始化函数
    function init() {
        // 设置 CSS 类
        toggleSSRVisibility();
        
        // 直接隐藏菜单项
        hideSSRMenuItems();
        
        // 开始观察 DOM 变化
        observeMenuChanges();
        
        // 监听 URL 变化（用于 SPA 应用）
        window.addEventListener('popstate', function() {
            setTimeout(function() {
                toggleSSRVisibility();
                hideSSRMenuItems();
            }, 100);
        });
    }
    
    // 等待 DOM 加载完成
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // 额外的延迟执行，确保在 LuCI 菜单加载后执行
    setTimeout(function() {
        hideSSRMenuItems();
    }, 500);
    
    setTimeout(function() {
        hideSSRMenuItems();
    }, 1000);
    
})();

// 为了兼容性，也提供全局函数
window.toggleSSRMenu = function(show) {
    const body = document.body;
    if (show) {
        body.classList.add('show-ssr');
    } else {
        body.classList.remove('show-ssr');
    }
};