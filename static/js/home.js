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

  // Функция для форматирования размера файла
  const formatFileSize = function(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  // Функция для получения списка уже загруженных файлов
  const getUploadedFiles = function() {
    const files = [];
    const tbody = document.getElementById('filesTableBody');
    if (tbody) {
      const rows = tbody.querySelectorAll('tr');
      rows.forEach(function(row) {
        const filename = row.dataset.filename;
        const fileSize = row.dataset.fileSize;
        if (filename && fileSize) {
          files.push({
            name: filename,
            size: fileSize
          });
        }
      });
    }
    return files;
  };

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

  // Функция для показа ошибки
  const showError = function(message) {
    const alertPlaceholder = document.getElementById('uploadAlerts');
    if (alertPlaceholder) {
      alertPlaceholder.innerHTML = '<div class="alert alert-danger alert-timed mb-0" role="alert" data-duration="5000">' +
        '<span>' + message + '</span>' +
        '<div class="alert-progress alert-progress-danger"></div>' +
        '</div>';
      
      // Запускаем таймер для автоматического скрытия
      const alert = alertPlaceholder.querySelector('.alert-timed');
      if (alert) {
        const duration = parseInt(alert.dataset.duration, 10) || 5000;
        const progressBar = alert.querySelector('.alert-progress');
        if (progressBar) {
          progressBar.style.animationDuration = duration + 'ms';
        }
        setTimeout(function() {
          alert.classList.add('fade-out');
          setTimeout(function() {
            alert.remove();
          }, 300);
        }, duration);
      }
    }
  };

  // Переменная для отслеживания последнего отправленного файла (чтобы предотвратить двойную отправку)
  let isUploading = false;

  fileInput.addEventListener('change', function () {
    if (fileInput.files && fileInput.files.length > 0) {
      const file = fileInput.files[0];
      const fileName = file.name;
      const fileSize = file.size;
      const maxSize = 512 * 1024 * 1024; // 512 МБ в байтах

      // Проверка размера файла
      if (fileSize > maxSize) {
        showError('Файл слишком большой! Максимальный размер — 512 МБ. Выбранный файл: ' + formatFileSize(fileSize));
        fileInput.value = '';
        resetLabels();
        return;
      }

      // Проверка на дубликаты
      const uploadedFiles = getUploadedFiles();
      const duplicate = uploadedFiles.find(function(uploaded) {
        return uploaded.name === fileName && 
               Math.abs(parseFileSize(uploaded.size) - fileSize) < 1024; // Допуск 1KB
      });

      if (duplicate) {
        showError('Файл с именем "' + fileName + '" уже загружен. Выберите другой файл или переименуйте существующий.');
        fileInput.value = '';
        resetLabels();
        return;
      }

      labelPrimary.textContent = fileName;
      labelSecondary.textContent = formatFileSize(fileSize) + ' • нажмите, чтобы выбрать другой файл';
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

  // Валидация формы загрузки перед отправкой
  const uploadForm = document.getElementById('uploadForm');
  if (uploadForm) {
    uploadForm.addEventListener('submit', function(e) {
      if (!fileInput.files || fileInput.files.length === 0) {
        e.preventDefault();
        showError('Пожалуйста, выберите файл для загрузки.');
        return false;
      }

      const file = fileInput.files[0];
      const fileSize = file.size;
      const maxSize = 512 * 1024 * 1024; // 512 МБ

      // Повторная проверка размера перед отправкой
      if (fileSize > maxSize) {
        e.preventDefault();
        showError('Файл слишком большой! Максимальный размер — 512 МБ.');
        return false;
      }

      // Проверка на дубликаты перед отправкой
      const uploadedFiles = getUploadedFiles();
      const duplicate = uploadedFiles.find(function(uploaded) {
        return uploaded.name === file.name && 
               Math.abs(parseFileSize(uploaded.size) - fileSize) < 1024;
      });

      if (duplicate) {
        e.preventDefault();
        showError('Файл с именем "' + file.name + '" уже загружен. Выберите другой файл или переименуйте существующий.');
        return false;
      }

      // Предотвращаем двойную отправку
      if (isUploading) {
        e.preventDefault();
        showError('Идет загрузка файла. Пожалуйста, подождите...');
        return false;
      }

      // Устанавливаем флаг загрузки
      isUploading = true;
      
      // Сбрасываем флаг через 10 секунд (на случай, если что-то пошло не так)
      setTimeout(function() {
        isUploading = false;
      }, 10000);
    });
  }
});