/**
 * WEBSITE: https://themefisher.com
 * TWITTER: https://twitter.com/themefisher
 * FACEBOOK: https://www.facebook.com/themefisher
 * GITHUB: https://github.com/themefisher/
 */

(function ($) {
  'use strict';

  /* ========================================================================= */
  /*	Page Preloader
  /* ========================================================================= */
  $(window).on('load', function () {
    $('#preloader').fadeOut('slow', function () {
      $(this).remove();
    });
  });

  // navbarDropdown
	if ($(window).width() < 992) {
		$('#navigation .dropdown-toggle').on('click', function () {
			$(this).siblings('.dropdown-menu').animate({
				height: 'toggle'
			}, 300);
		});
  }
  
  /* ========================================================================= */
  /*	Hero Slider
  /* ========================================================================= */
  function initializeHeroSlider() {
    $('.hero-slider').slick({
      autoplay: true,
      infinite: true,
      arrows: true,
      prevArrow: '<button type=\'button\' class=\'prevArrow\'></button>',
      nextArrow: '<button type=\'button\' class=\'nextArrow\'></button>',
      dots: false,
      autoplaySpeed: 7000,
      pauseOnFocus: false,
      pauseOnHover: false,
      responsive: [{
        breakpoint: 768,
        settings: {
          arrows: false,
          dots: false
        }
      }]
    });

    // 确保横幅内容可见
    $('.hero-area').css('opacity', '1');
    $('.hero-area h1, .hero-area p, .hero-area a').css({
      'opacity': '1',
      'transform': 'none'
    });
  }

  /* ========================================================================= */
  /*	导航栏滚动效果
  /* ========================================================================= */
  function handleNavigation() {
    const nav = document.querySelector('.navigation');
    const logoDefault = document.querySelector('.logo-default');
    const logoWhite = document.querySelector('.logo-white');
    
    if (!nav || !logoDefault || !logoWhite) return;

    function updateNavigation() {
      if (window.scrollY > 50) {
        nav.classList.remove('top');
        nav.classList.add('scrolled');
        logoDefault.style.display = 'block';
        logoWhite.style.display = 'none';
      } else {
        nav.classList.add('top');
        nav.classList.remove('scrolled');
        logoDefault.style.display = 'none';
        logoWhite.style.display = 'block';
      }
    }

    // 监听滚动事件
    window.addEventListener('scroll', updateNavigation);

    // 页面加载时初始化导航栏状态
    nav.classList.add('top');
    updateNavigation();
  }

  /* ========================================================================= */
  /*	价格方案功能
  /* ========================================================================= */
  function initializePricing() {
    // 确保价格卡片初始可见
    $('.pricing-card').css({
      'opacity': '1',
      'transform': 'none'
    });

    // 价格卡片悬停效果
    $('.pricing-card').hover(
      function() {
        $(this).addClass('hover');
      },
      function() {
        $(this).removeClass('hover');
      }
    );

    // 滚动动画
    function checkPricingAnimation() {
      var windowBottom = $(window).scrollTop() + $(window).height();
      
      $('.pricing-card').each(function() {
        var elementTop = $(this).offset().top;
        
        if (elementTop <= windowBottom) {
          $(this).addClass('animate');
        }
      });
    }

    // 初始检查
    checkPricingAnimation();

    // 滚动时检查
    $(window).scroll(checkPricingAnimation);

    // 点击购买按钮的事件处理
    $('.btn-purchase').click(function(e) {
      // 如果是免费体验按钮，不需要额外处理，让它触发模态框
      if ($(this).closest('.pricing-card').find('h3').text() === '免费体验') {
        return;
      }
      
      // 其他购买按钮的处理
      const price = $(this).closest('.pricing-card').find('.price').text();
      const plan = $(this).closest('.pricing-card').find('h3').text();
      
      // 可以在这里添加购买相关的统计代码
      if (window._hmt) {
        window._hmt.push(['_trackEvent', '购买按钮', '点击', `${plan}-${price}`]);
      }
    });
  }

  /* ========================================================================= */
  /*	表单处理功能
  /* ========================================================================= */
  function initializeForm() {
    const form = document.getElementById('downloadForm');
    const scaleGroup = document.getElementById('scale-group');
    const companyRadios = document.getElementsByName('company');

    if (!form || !scaleGroup || !companyRadios.length) return;

    // 默认显示规模大小
    scaleGroup.style.display = 'block';

    // 监听公司/个人单选按钮的变化
    companyRadios.forEach(radio => {
      radio.addEventListener('change', function() {
        if (this.value === '个人') {
          scaleGroup.style.display = 'none';
          document.getElementById('scale').removeAttribute('required');
        } else {
          scaleGroup.style.display = 'block';
          document.getElementById('scale').setAttribute('required', 'required');
        }
      });
    });

    // 表单提交处理
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const formData = new FormData(e.target);
      const data = Object.fromEntries(formData.entries());
      
      try {
        const response = await fetch('https://stellar.ai-yy.com/api/submit-form', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        });
        
        if (response.ok) {
          // 显示成功提示
          $('#submitToast').toast('show');
          
          // 清空表单
          e.target.reset();
          // 关闭模态框
          $('#downloadModal').modal('hide');

          // 百度统计
          if (window._hmt) {
            window._hmt.push(['_trackEvent', '表单提交', '成功']);
          }
        } else {
          throw new Error('提交失败');
        }
      } catch (error) {
        console.error('Error:', error);
        alert('提交失败，请稍后重试。');
        
        // 百度统计
        if (window._hmt) {
          window._hmt.push(['_trackEvent', '表单提交', '失败', error.message]);
        }
      }
    });
  }

  /* ========================================================================= */
  /*	在 DOM 加载完成后初始化所有功能
  /* ========================================================================= */
  $(document).ready(function() {
    handleNavigation();
    initializeHeroSlider();
    initializePricing();
    initializeForm();
  });

})(jQuery);
