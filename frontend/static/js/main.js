/**
 * 自然物种查询门户 - 主 JavaScript 文件
 */

// 设置自动补全功能
function setupAutocomplete(inputId, suggestionsId) {
    const input = document.getElementById(inputId);
    const suggestions = document.getElementById(suggestionsId);
    
    if (!input || !suggestions) return;
    
    let debounceTimer;
    let currentFocus = -1;
    
    input.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        const query = this.value.trim();
        
        if (query.length < 2) {
            suggestions.style.display = 'none';
            return;
        }
        
        debounceTimer = setTimeout(async () => {
            try {
                const response = await fetch(`/api/autocomplete?q=${encodeURIComponent(query)}&per_page=10`);
                const data = await response.json();
                
                if (data.success && data.suggestions.length > 0) {
                    renderSuggestions(data.suggestions, suggestions, input);
                } else {
                    suggestions.style.display = 'none';
                }
            } catch (error) {
                console.error('Autocomplete error:', error);
            }
        }, 300);
    });
    
    // 键盘导航
    input.addEventListener('keydown', function(e) {
        const items = suggestions.querySelectorAll('.suggestion-item');
        
        if (e.key === 'ArrowDown') {
            currentFocus++;
            addActive(items);
            e.preventDefault();
        } else if (e.key === 'ArrowUp') {
            currentFocus--;
            addActive(items);
            e.preventDefault();
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (currentFocus > -1 && items[currentFocus]) {
                items[currentFocus].click();
            } else {
                // 提交表单
                input.closest('form')?.submit();
            }
        } else if (e.key === 'Escape') {
            suggestions.style.display = 'none';
        }
    });
    
    // 点击外部关闭
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.style.display = 'none';
        }
    });
    
    function addActive(items) {
        if (!items) return;
        removeActive(items);
        if (currentFocus >= items.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = items.length - 1;
        items[currentFocus].classList.add('active');
    }
    
    function removeActive(items) {
        items.forEach(item => item.classList.remove('active'));
    }
}

// 渲染建议列表
function renderSuggestions(suggestionsData, container, input) {
    container.innerHTML = suggestionsData.map((s, index) => `
        <div class="suggestion-item" data-id="${s.id}" data-index="${index}">
            <div class="suggestion-name">
                ${s.display_name || s.name}
            </div>
            <div class="suggestion-meta">
                ${s.rank} • ${s.iconic_taxon || 'Unknown'} • ${formatNumber(s.observations_count)} 次观察
            </div>
        </div>
    `).join('');
    
    container.style.display = 'block';
    
    // 绑定点击事件
    container.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('click', function() {
            const taxonId = this.dataset.id;
            window.location.href = `/species/${taxonId}`;
        });
    });
}

// 格式化数字
function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

// 格式化日期
function formatDate(dateString) {
    if (!dateString) return '未知日期';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 获取当前位置
function getCurrentPosition() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('浏览器不支持地理定位'));
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            position => resolve({
                lat: position.coords.latitude,
                lng: position.coords.longitude
            }),
            error => reject(error)
        );
    });
}

// 复制到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        return true;
    } catch (err) {
        console.error('复制失败:', err);
        return false;
    }
}

// 显示提示消息
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 200px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// 图片懒加载
function setupLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // 回退方案
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// 初始化工具提示
function initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
    }
}

// 初始化弹出框
function initPopovers() {
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    if (typeof bootstrap !== 'undefined') {
        popoverTriggerList.forEach(el => new bootstrap.Popover(el));
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 设置导航栏搜索框的自动补全
    setupAutocomplete('nav-search', 'search-suggestions');
    
    // 初始化工具提示
    initTooltips();
    
    // 初始化弹出框
    initPopovers();
    
    // 设置图片懒加载
    setupLazyLoading();
    
    console.log('🌿 自然物种查询门户已加载');
});

// 导出全局函数
window.NaturePortal = {
    setupAutocomplete,
    formatNumber,
    formatDate,
    debounce,
    throttle,
    getCurrentPosition,
    copyToClipboard,
    showToast,
    setupLazyLoading
};
