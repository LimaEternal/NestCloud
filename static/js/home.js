document.addEventListener('DOMContentLoaded', function () {
  const fileInput = document.getElementById('fileInput');
  const selectFileBtn = document.getElementById('selectFileBtn');
  const labelPrimary = document.getElementById('fileLabelPrimary');
  const labelSecondary = document.getElementById('fileLabelSecondary');

  const resetLabels = function () {
    labelPrimary.textContent = 'Нажмите для выбора файла';
    labelSecondary.textContent = '';
  };

  selectFileBtn.addEventListener('click', function () {
    fileInput.click();
  });

  fileInput.addEventListener('change', function () {
    if (fileInput.files && fileInput.files.length > 0) {
      const fileName = fileInput.files[0].name;
      labelPrimary.textContent = fileName;
      labelSecondary.textContent = 'нажмите, чтобы выбрать другой файл';
    } else {
      resetLabels();
    }
  });

  const timedAlerts = document.querySelectorAll('.alert-timed');
  timedAlerts.forEach(function (alert) {
    const duration = parseInt(alert.dataset.duration, 10) || 5000;
    const progressBar = alert.querySelector('.alert-progress');
    if (progressBar) {
      progressBar.style.animationDuration = duration + 'ms';
    }

    setTimeout(function () {
      alert.classList.add('fade-out');
      setTimeout(function () {
        alert.remove();
      }, 300);
    }, duration);
  });

  // Обработка модального окна переименования
  const renameModal = document.getElementById('renameModal');
  if (renameModal) {
    const newFilenameInput = renameModal.querySelector('#newFilename');
    const renameForm = renameModal.querySelector('#renameForm');
    
    renameModal.addEventListener('show.bs.modal', function (event) {
      const button = event.relatedTarget;
      const fileId = button.getAttribute('data-file-id');
      const fileName = button.getAttribute('data-file-name');
      
      const currentFileNameSpan = renameModal.querySelector('#currentFileName');
      
      // Извлекаем расширение файла
      const lastDotIndex = fileName.lastIndexOf('.');
      let fileExtension = '';
      let nameWithoutExtension = fileName;
      
      if (lastDotIndex !== -1 && lastDotIndex < fileName.length - 1) {
        fileExtension = fileName.substring(lastDotIndex);
        nameWithoutExtension = fileName.substring(0, lastDotIndex);
      }
      
      // Сохраняем расширение в data-атрибуте
      newFilenameInput.dataset.extension = fileExtension;
      
      // Показываем только имя без расширения
      newFilenameInput.value = nameWithoutExtension;
      currentFileNameSpan.textContent = fileName;
      
      // Устанавливаем действие формы
      renameForm.action = '/rename/' + fileId;
    });
    
    // Автоматически добавляем расширение перед отправкой формы
    if (renameForm) {
      const hiddenInput = renameModal.querySelector('#newFilenameHidden');
      
      renameForm.addEventListener('submit', function(e) {
        const extension = newFilenameInput.dataset.extension || '';
        let currentValue = newFilenameInput.value.trim();
        
        // Удаляем расширение, если пользователь его добавил
        if (extension && currentValue.toLowerCase().endsWith(extension.toLowerCase())) {
          currentValue = currentValue.substring(0, currentValue.length - extension.length);
        }
        
        // Добавляем оригинальное расширение в скрытое поле для отправки
        if (extension && currentValue) {
          hiddenInput.value = currentValue + extension;
        } else {
          hiddenInput.value = currentValue;
        }
      });
    }
  }
});