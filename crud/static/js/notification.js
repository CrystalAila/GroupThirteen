function closeToast(toastId) {
    const toast = document.getElementById(toastId);
    if (toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide toasts after 3 seconds with smooth animation
    setTimeout(() => {
        document.querySelectorAll('[id^="toast-"]').forEach(el => {
            if (el.id) {
                closeToast(el.id);
            }
        });
    }, 3000);

    // Handle data-dismiss-target buttons with smooth animations
    document.querySelectorAll('[data-dismiss-target]').forEach(button => {
        button.addEventListener('click', function () {
            const targetId = this.getAttribute('data-dismiss-target');
            const target = document.querySelector(targetId);
            if (target) {
                // Check if it's a toast element and use smooth animation
                if (target.id && target.id.startsWith('toast-')) {
                    closeToast(target.id);
                } else {
                    // Fallback for non-toast elements
                    target.style.display = 'none';
                }
            }
        });
    });
});