/**
 * WEBSITE: https://themefisher.com
 * TWITTER: https://twitter.com/themefisher
 * FACEBOOK: https://www.facebook.com/themefisher
 * GITHUB: https://github.com/themefisher/
 */

(function ($) {
  'use strict';

  /* ========================================================================= */
  /*	在 DOM 加载完成后初始化所有功能
  /* ========================================================================= */
  $(document).ready(function() {
    // 初始化 AOS
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 800,
        once: true
      });
    }
    
    handleNavigation();
    initializeHeroSlider();
    initializePricing();
  });

  /* ========================================================================= */
  /*	导航栏滚动效果
  /* ========================================================================= */
  function handleNavigation() {
    const nav = document.querySelector('.navigation');
    const logoDefault = document.querySelector('.logo-default');
    const logoWhite = document.querySelector('.logo-white');

    if (!nav || !logoDefault || !logoWhite) return;

    function updateNav() {
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

    // 初始化状态
    nav.classList.add('top');
    updateNav();

    // 监听滚动事件
    window.addEventListener('scroll', updateNav);
  }

  /* ========================================================================= */
  /*	主页横幅滑块
  /* ========================================================================= */
  function initializeHeroSlider() {
    const heroSlider = $('.hero-slider');
    if (heroSlider.length) {
      heroSlider.slick({
        autoplay: true,
        infinite: true,
        arrows: true,
        prevArrow: '<button type="button" class="prevArrow"></button>',
        nextArrow: '<button type="button" class="nextArrow"></button>',
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

      // 初始化滑块动画
      heroSlider.slickAnimation();

      // 确保第一个滑块的文字可见
      setTimeout(() => {
        const firstSlide = heroSlider.find('.slick-current');
        firstSlide.find('[data-animation-in]').each(function() {
          const $this = $(this);
          const animationIn = $this.data('animation-in');
          $this.css('opacity', '1').addClass('animated ' + animationIn);
        });
      }, 100);
    }
  }

  /* ========================================================================= */
  /*	价格方案功能
  /* ========================================================================= */
  function initializePricing() {
    // 点击购买按钮的事件处理
    $('.btn-purchase').click(function(e) {
      const price = $(this).closest('.pricing-card').find('.price').text();
      const plan = $(this).closest('.pricing-card').find('h3').text();
      
      // 添加购买相关的统计代码
      if (window._hmt) {
        window._hmt.push(['_trackEvent', '购买按钮', '点击', `${plan}-${price}`]);
      }
    });
  }

  /* ========================================================================= */
  /*	移动端菜单处理
  /* ========================================================================= */
  // 点击空白区域关闭菜单
  $(document).click(function (event) {
    var clickover = $(event.target);
    var _opened = $(".navbar-collapse").hasClass("show");
    if (_opened === true && !clickover.hasClass("navbar-toggler")) {
      $(".navbar-toggler").click();
    }
  });

})(jQuery);