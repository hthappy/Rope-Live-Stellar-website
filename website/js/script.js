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
  
  //Hero Slider
  $('.hero-slider').slick({
    autoplay: true,
    infinite: true,
    arrows: true,
    prevArrow: '<button type=\'button\' class=\'prevArrow\'></button>',
    nextArrow: '<button type=\'button\' class=\'nextArrow\'></button>',
    dots: false,
    autoplaySpeed: 7000,
    pauseOnFocus: false,
    pauseOnHover: false
  });
  $('.hero-slider').slickAnimation();

  /* ========================================================================= */
  /*	Portfolio Filtering Hook
  /* =========================================================================  */
  // filter
  setTimeout(function(){
    var containerEl = document.querySelector('.filtr-container');
    var filterizd;
    if (containerEl) {
      filterizd = $('.filtr-container').filterizr({});
    }
  }, 500);

  /* ========================================================================= */
  /*	Testimonial Carousel
  /* =========================================================================  */
  //Init the slider
  $('.testimonial-slider').slick({
    infinite: true,
    arrows: false,
    autoplay: true,
    autoplaySpeed: 2000
  });


  /* ========================================================================= */
  /*	Clients Slider Carousel
  /* =========================================================================  */
  //Init the slider
  $('.clients-logo-slider').slick({
    infinite: true,
    arrows: false,
    autoplay: true,
    autoplaySpeed: 2000,
    slidesToShow: 5,
    slidesToScroll: 1,
    responsive: [{
      breakpoint: 1024,
      settings: {
        slidesToShow: 4,
        slidesToScroll: 1,
        infinite: true,
        dots: false
      }
    },
    {
      breakpoint: 480,
      settings: {
        slidesToShow: 3,
        slidesToScroll: 1,
        arrows: false
      }
    }
    ]
  });

  /* ========================================================================= */
  /*	Company Slider Carousel
  /* =========================================================================  */
  $('.company-gallery').slick({
    infinite: true,
    arrows: false,
    autoplay: true,
    autoplaySpeed: 2000,
    slidesToShow: 5,
    slidesToScroll: 1,
    responsive: [{
      breakpoint: 1024,
      settings: {
        slidesToShow: 4,
        slidesToScroll: 1,
        infinite: true,
        dots: false
      }
    },
    {
      breakpoint: 667,
      settings: {
        slidesToShow: 3,
        slidesToScroll: 1,
        arrows: false
      }
    },
    {
      breakpoint: 480,
      settings: {
        slidesToShow: 2,
        slidesToScroll: 1,
        arrows: false
      }
    }
    ]
  });

  /* ========================================================================= */
  /*	On scroll fade/bounce effect
  /* ========================================================================= */
  var scroll = new SmoothScroll('a[href*="#"]');

  // -----------------------------
  //  Count Up
  // -----------------------------
  function counter() {
    var oTop;
    if ($('.counter').length !== 0) {
      oTop = $('.counter').offset().top - window.innerHeight;
    }
    if ($(window).scrollTop() > oTop) {
      $('.counter').each(function () {
        var $this = $(this),
          countTo = $this.attr('data-count');
        $({
          countNum: $this.text()
        }).animate({
          countNum: countTo
        }, {
          duration: 1000,
          easing: 'swing',
          step: function () {
            $this.text(Math.floor(this.countNum));
          },
          complete: function () {
            $this.text(this.countNum);
          }
        });
      });
    }
  }
  // -----------------------------
  //  On Scroll
  // -----------------------------
  $(window).scroll(function () {
    counter();

    var scroll = $(window).scrollTop();
    if (scroll > 50) {
      $('.navigation').addClass('sticky-header');
    } else {
      $('.navigation').removeClass('sticky-header');
    }
  });

  // 表单提交处理
  document.addEventListener('DOMContentLoaded', function() {
    // 创建提示框
    const alertDiv = document.createElement('div');
    alertDiv.className = 'floating-alert';
    alertDiv.innerHTML = `
      <div class="alert-content">
        <i class="fas fa-check-circle"></i>
        <p>申请已提交成功！<br>我们会尽快审核并通过邮�����回复您。</p>
        <button class="alert-confirm">确认</button>
      </div>
    `;
    document.body.appendChild(alertDiv);
  
    const form = document.getElementById('downloadForm');
    const scaleGroup = document.getElementById('scale-group');
    const companyRadios = document.getElementsByName('company');

    // 默认隐藏规模大小
    scaleGroup.style.display = 'none';

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

    if (form) {
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
            // 显示悬浮提示
            alertDiv.classList.add('show');
            
            // 清空表单
            e.target.reset();
            // 关闭模态框
            $('#downloadModal').modal('hide');
  
            // 点击确认按钮后跳转
            const confirmBtn = alertDiv.querySelector('.alert-confirm');
            confirmBtn.addEventListener('click', function() {
              alertDiv.classList.remove('show');
              window.location.href = 'https://pan.baidu.com/s/15TcjRMjhUjkyrhK4ROMpsg?pwd=39bv';
            });
          } else {
            throw new Error('提交失败');
          }
        } catch (error) {
          console.error('Error:', error);
          alert('提交失败，请稍后重试。');
        }
      });
    }
  });

})(jQuery);

// 处理导航栏状态
function updateNavbarState() {
  const navbar = document.querySelector('.navbar');
  const scrolled = window.scrollY > 50;
  
  if (scrolled) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
}

// 监听滚动事件
window.addEventListener('scroll', function() {
  const navbar = document.querySelector('.navbar');
  
  if (window.scrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// 监听窗口大小变化
window.addEventListener('resize', updateNavbarState);

// 页面加载时初始化导航栏状态
document.addEventListener('DOMContentLoaded', function() {
  const navbar = document.querySelector('.navbar');
  
  // 触发一次滚动检查
  if (window.scrollY > 50) {
    navbar.classList.add('scrolled');
  }
});

// 添加版本切换的初始化和事件处理
$(document).ready(function() {
  // 初始化标签页
  $('#basic').addClass('show active');
  
  // 为版本切换按钮添加点击事件
  $('.btn-version').on('click', function(e) {
    e.preventDefault();
    
    // 移除所有按钮的 active 类
    $('.btn-version').removeClass('active');
    // 为当前点击的按钮添加 active 类
    $(this).addClass('active');
    
    // 获取目标面板
    const target = $(this).data('target');
    
    // 隐藏所有面板
    $('.tab-pane').removeClass('show active');
    // 显示目标面板
    $(target).addClass('show active');
  });
});

// 移动端导航栏处理
$(document).ready(function() {
  // 处理导航栏折叠按钮动画
  $('.navbar-toggler').on('click', function() {
    $(this).toggleClass('is-active');
    $('body').toggleClass('menu-open');
    
    const isExpanded = $(this).attr('aria-expanded') === 'true';
    
    if (!isExpanded) {
      // 菜单打开时的动画
      $('.nav-item').each(function(index) {
        $(this).css({
          'opacity': '0',
          'transform': 'translateY(20px)',
          'transition-delay': (index * 0.1) + 's'
        });
        setTimeout(() => {
          $(this).css({
            'opacity': '1',
            'transform': 'translateY(0)'
          });
        }, 100);
      });
    } else {
      // 菜单关闭时重置样式
      $('.nav-item').css({
        'opacity': '',
        'transform': '',
        'transition-delay': ''
      });
    }
  });

  // 点击导航链接时自动收起菜单
  $('.nav-link').on('click', function() {
    if ($(window).width() < 992) {
      const bsCollapse = new bootstrap.Collapse(document.getElementById('navbarNav'), {
        toggle: false
      });
      bsCollapse.hide();
      $('.navbar-toggler').removeClass('is-active').attr('aria-expanded', 'false');
      $('body').removeClass('menu-open');
    }
  });

  // 点击页面空白处关闭菜单
  $(document).on('click', function(e) {
    if ($(window).width() < 992) {
      if (!$(e.target).closest('.navbar').length && $('#navbarNav').hasClass('show')) {
        const bsCollapse = new bootstrap.Collapse(document.getElementById('navbarNav'), {
          toggle: false
        });
        bsCollapse.hide();
        $('.navbar-toggler').removeClass('is-active').attr('aria-expanded', 'false');
        $('body').removeClass('menu-open');
      }
    }
  });

  // 处理窗口大小改变
  $(window).on('resize', function() {
    if ($(window).width() >= 992) {
      $('body').removeClass('menu-open');
      $('#navbarNav').removeClass('show');
      $('.navbar-toggler').removeClass('is-active').attr('aria-expanded', 'false');
      $('.nav-item').css({
        'opacity': '',
        'transform': '',
        'transition-delay': ''
      });
    }
  });

  // 处理视频演示标签页
  $('.demo-tabs .nav-link').on('click', function(e) {
    e.preventDefault();
    $(this).tab('show');
  });

  // 处理视频容器大小
  function adjustVideoContainers() {
    $('.video-container').each(function() {
      const width = $(this).width();
      $(this).css('height', width * 0.5625); // 16:9 aspect ratio
    });
  }

  // 在页面加载和窗口调整时调整视频容器大小
  adjustVideoContainers();
  $(window).on('resize', adjustVideoContainers);
});

// 处理移动端模态框
$(document).ready(function() {
  // 调整模态框在移动端的显示
  if ($(window).width() < 768) {
    $('.modal-dialog').css('margin', '10px');
  }

  // 处理表单在移动端的提交
  $('#downloadForm').on('submit', function(e) {
    e.preventDefault();
    
    // 在移动端添加加载状态
    const submitBtn = $(this).find('button[type="submit"]');
    const originalText = submitBtn.html();
    submitBtn.html('<i class="fas fa-spinner fa-spin"></i> 提交中...');
    submitBtn.prop('disabled', true);

    // 模拟表单提交
    setTimeout(function() {
      submitBtn.html(originalText);
      submitBtn.prop('disabled', false);
      $('#downloadModal').modal('hide');
      
      // 示成功提示
      $('.floating-alert').addClass('show');
    }, 1500);
  });
});