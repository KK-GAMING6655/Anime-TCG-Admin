document.addEventListener('DOMContentLoaded', () => {
    const cardForm = document.getElementById('cardForm');
    const imageTypeRadios = document.querySelectorAll('input[name="image_type"]');
    const fileInputGroup = document.getElementById('fileInputGroup');
    const urlInputGroup = document.getElementById('urlInputGroup');

    // Toggle between File Upload and Image URL inputs
    imageTypeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'file') {
                fileInputGroup.classList.remove('hidden');
                urlInputGroup.classList.add('hidden');
            } else {
                fileInputGroup.classList.add('hidden');
                urlInputGroup.classList.remove('hidden');
            }
        });
    });

    // Form Submission Event Listener
    if (cardForm) {
        cardForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn ? submitBtn.innerText : 'Add Card';

            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerText = "Adding Card...";
            }

            try {
                const response = await fetch('/api/add-card', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();

                if (response.ok && data.success) {
                    const successMsg = data.message || `Card created successfully!`;
                    showToast('✅ ' + successMsg, true);
                    
                    // Reset form fields
                    cardForm.reset();
                    
                    // Reset inputs display to default
                    if (fileInputGroup && urlInputGroup) {
                        fileInputGroup.classList.remove('hidden');
                        urlInputGroup.classList.add('hidden');
                    }
                } else {
                    // Extract error message safely to prevent 'undefined'
                    const errorMsg = data.message || data.error || `Server Error (${response.status})`;
                    showToast('❌ ' + errorMsg, false);
                }
            } catch (err) {
                console.error('Submission Error:', err);
                showToast('❌ Could not connect to server.', false);
            } finally {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerText = originalBtnText;
                }
            }
        });
    }
});

/**
 * Custom Toast Notification System
 */
function showToast(message, isSuccess = true) {
    let toast = document.getElementById('toast');

    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.right = '20px';
        toast.style.padding = '12px 20px';
        toast.style.borderRadius = '8px';
        toast.style.color = '#ffffff';
        toast.style.fontWeight = '600';
        toast.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.3)';
        toast.style.zIndex = '9999';
        toast.style.transition = 'all 0.3s ease-in-out';
        document.body.appendChild(toast);
    }

    toast.style.backgroundColor = isSuccess ? '#10B981' : '#EF4444';
    toast.innerText = message;
    toast.style.display = 'block';

    setTimeout(() => {
        toast.style.display = 'none';
    }, 4500);
            }
        
