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

  // Функция сортировки файлов
  const sortFiles = function(sortType) {
    const tbody = document.getElementById('filesTableBody');
    if (!tbody) return;

    const rows = Array.from(tbody.querySelectorAll('tr'));
    if (rows.length === 0) return;

    // Функция для парсинга размера файла в байты
    const parseFileSize = function(sizeStr) {
      if (!sizeStr) return 0;
      const units = {
        'B': 1,
        'KB': 1024,
        'MB': 1024 * 1024,
        'GB': 1024 * 1024 * 1024,
        'TB': 1024 * 1024 * 1024 * 1024
      };
      const match = sizeStr.trim().match(/^([\d.]+)\s*([A-Z]+)$/i);
      if (!match) return 0;
      const value = parseFloat(match[1]);
      const unit = match[2].toUpperCase();
      return value * (units[unit] || 1);
    };

    // Функция для парсинга времени
    const parseTime = function(timeStr) {
      return new Date(timeStr).getTime();
    };

    // Сортировка
    rows.sort(function(a, b) {
      let comparison = 0;
      
      if (sortType.startsWith('name-')) {
        const nameA = (a.dataset.filename || '').toLowerCase();
        const nameB = (b.dataset.filename || '').toLowerCase();
        comparison = nameA.localeCompare(nameB, 'ru');
        if (sortType === 'name-desc') comparison = -comparison;
      } else if (sortType.startsWith('size-')) {
        const sizeA = parseFileSize(a.dataset.fileSize);
        const sizeB = parseFileSize(b.dataset.fileSize);
        comparison = sizeA - sizeB;
        if (sortType === 'size-desc') comparison = -comparison;
      } else if (sortType.startsWith('time-')) {
        const timeA = parseTime(a.dataset.uploadTime);
        const timeB = parseTime(b.dataset.uploadTime);
        comparison = timeA - timeB;
        if (sortType === 'time-desc') comparison = -comparison;
      }
      
      return comparison;
    });

    // Очищаем tbody и добавляем отсортированные строки
    tbody.innerHTML = '';
    rows.forEach(function(row) {
      tbody.appendChild(row);
    });
  };

  // Обработчики для кнопок сортировки
  const sortDropdownItems = document.querySelectorAll('#sortDropdown .dropdown-item');
  sortDropdownItems.forEach(function(item) {
    item.addEventListener('click', function(e) {
      e.preventDefault();
      const sortType = this.dataset.sort;
      if (sortType) {
        sortFiles(sortType);
        // Обновляем текст кнопки
        const sortBtn = document.getElementById('sortBtn');
        if (sortBtn) {
          const icon = sortBtn.querySelector('i');
          const text = this.textContent.trim();
          sortBtn.innerHTML = icon ? icon.outerHTML + ' ' + text : text;
        }
      }
    });
  });
});