/**
 * ShadowSocksR 和 FRP 菜单动态控制脚本
 * 根据 URL 参数动态显示/隐藏 ShadowSocksR 和 FRP 菜单项
 */

(function() {
    'use strict';
    
    // 检查 URL 参数
    function checkShowSSRParameter() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.has('show_ssr') && urlParams.get('show_ssr') === '1';
    }
    
    // 检查是否显示 FRP 菜单
    function checkShowFRPParameter() {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.has('show_frp') && urlParams.get('show_frp') === '1';
    }
    
    // 添加或移除 CSS 类
    function toggleServicesVisibility() {
        const body = document.body;
        
        if (checkShowSSRParameter()) {
            body.classList.add('show-ssr');
            console.log('ShadowSocksR menu enabled via URL parameter');
        } else {
            body.classList.remove('show-ssr');
            console.log('ShadowSocksR menu hidden (no show_ssr parameter)');
        }
        
        if (checkShowFRPParameter()) {
            body.classList.add('show-frp');
            console.log('FRP menu enabled via URL parameter');
        } else {
            body.classList.remove('show-frp');
            console.log('FRP menu hidden (no show_frp parameter)');
        }
    }
    
    // 直接隐藏 ShadowSocksR 和 FRP 菜单项
    function hideServiceMenuItems() {
        // 隐藏 ShadowSocksR 菜单项
        if (!checkShowSSRParameter()) {
            // 只在菜单页面隐藏菜单项，不影响具体功能页面的显示
            if (!window.location.pathname.includes('/admin/services/shadowsocksr')) {
                hideMenuByService('shadowsocksr', 'ShadowSocksR');
            }
        }
        
        // 隐藏 FRP 菜单项
        if (!checkShowFRPParameter()) {
            // 只在菜单页面隐藏菜单项，不影响具体功能页面的显示
            if (!window.location.pathname.includes('/admin/services/frp')) {
                hideMenuByService('frp', 'FRP');
            }
        }
    }
    
    // 通用的隐藏菜单函数
    function hideMenuByService(serviceName, displayName) {
        // 查找并隐藏指定服务相关的菜单项
        const selectors = [
            `a[data-title*="${displayName}"]`,
            `a[data-title*="${serviceName}"]`,
            `a[href*="/admin/services/${serviceName}"]`
        ];
        
        selectors.forEach(selector => {
            try {
                const elements = document.querySelectorAll(selector);
                elements.forEach(element => {
                    // 只隐藏指定服务相关的链接
                    const href = element.getAttribute('href') || '';
                    const title = element.getAttribute('data-title') || '';
                    const text = element.textContent || element.innerText || '';
                    
                    // 确保只隐藏指定服务相关的项目
                    if (href.includes(serviceName) || 
                        title.toLowerCase().includes(serviceName.toLowerCase()) ||
                        text.includes(displayName) ||
                        text.toLowerCase().includes(serviceName.toLowerCase())) {
                        
                        element.style.display = 'none';
                        
                        // 隐藏父级 li 元素，但要确保不影响其他服务
                        const parentLi = element.closest('li');
                        if (parentLi) {
                            // 检查父级 li 是否只包含当前服务相关内容
                            const otherLinks = parentLi.querySelectorAll(`a:not([href*="${serviceName}"]):not([data-title*="${serviceName}"])`);
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
                    setTimeout(hideServiceMenuItems, 100);
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
        toggleServicesVisibility();
        
        // 直接隐藏菜单项
        hideServiceMenuItems();
        
        // 开始观察 DOM 变化
        observeMenuChanges();
        
        // 监听 URL 变化（用于 SPA 应用）
        window.addEventListener('popstate', function() {
            setTimeout(function() {
                toggleServicesVisibility();
                hideServiceMenuItems();
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
        hideServiceMenuItems();
    }, 500);
    
    setTimeout(function() {
        hideServiceMenuItems();
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

window.toggleFRPMenu = function(show) {
    const body = document.body;
    if (show) {
        body.classList.add('show-frp');
    } else {
        body.classList.remove('show-frp');
    }
};