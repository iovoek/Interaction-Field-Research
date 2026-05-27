/**
 * canvas-recorder.js
 * Adds a hover-reveal "Record 10s" button to every animation container.
 * Records the canvas as an MP4 (H.264 via MediaRecorder) and auto-downloads.
 *
 * TO REMOVE: delete this script tag from each article and the canvas-recorder.css link.
 * Nothing else needs to change -- no animation code is modified.
 *
 * Supports:
 *   .art-viz-inner        (hero animations, canvas is first child)
 *   .art-viz-secondary    (secondary animations, canvas is first child)
 *   .inline-viz           (inline animations, canvas is appended by inline-viz.js)
 */
(function () {
  'use strict';

  var RECORD_DURATION_MS = 10000; // 10 seconds
  var MIME_PREFERENCE = [
    'video/mp4;codecs=avc1',
    'video/mp4',
    'video/webm;codecs=vp9',
    'video/webm;codecs=vp8',
    'video/webm'
  ];

  function getSupportedMime() {
    for (var i = 0; i < MIME_PREFERENCE.length; i++) {
      if (MediaRecorder.isTypeSupported(MIME_PREFERENCE[i])) {
        return MIME_PREFERENCE[i];
      }
    }
    return '';
  }

  function getExtension(mime) {
    if (mime.indexOf('mp4') !== -1) return 'mp4';
    return 'webm';
  }

  function findCanvas(container) {
    // For inline-viz, canvas is appended dynamically -- may not exist yet
    return container.querySelector('canvas');
  }

  function getFilename(container) {
    // Use data-scene, aria-label, or the canvas id to make a meaningful filename
    var scene = container.getAttribute('data-scene');
    if (scene) return 'animation-' + scene;
    var canvas = findCanvas(container);
    if (canvas && canvas.id) return 'animation-' + canvas.id;
    var label = container.querySelector('.art-viz-label, .art-viz-secondary-label');
    if (label) {
      return 'animation-' + label.textContent.trim().split('·')[0].trim().replace(/\s+/g, '-').replace(/[^a-z0-9\-]/gi, '').toLowerCase().slice(0, 40);
    }
    return 'animation-' + Date.now();
  }

  function createButton(container) {
    var btn = document.createElement('button');
    btn.className = 'rec-btn';
    btn.setAttribute('aria-label', 'Record 10-second video');
    btn.innerHTML =
      '<svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" style="display:inline-block;vertical-align:middle;margin-right:5px;">' +
        '<circle cx="6" cy="6" r="5" stroke="currentColor" stroke-width="1.2"/>' +
        '<circle cx="6" cy="6" r="2.5" fill="currentColor"/>' +
      '</svg>' +
      '<span class="rec-btn-text">Record 10s</span>';
    return btn;
  }

  function attachRecorder(container) {
    // Ensure position:relative on container so button can be positioned absolutely
    var pos = window.getComputedStyle(container).position;
    if (pos === 'static') container.style.position = 'relative';

    var btn = createButton(container);
    container.appendChild(btn);

    var mediaRecorder = null;
    var chunks = [];
    var timer = null;
    var isRecording = false;

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      if (isRecording) return;

      var canvas = findCanvas(container);
      if (!canvas) {
        btn.querySelector('.rec-btn-text').textContent = 'No canvas yet';
        setTimeout(function () { btn.querySelector('.rec-btn-text').textContent = 'Record 10s'; }, 2000);
        return;
      }

      var mime = getSupportedMime();
      if (!mime) {
        btn.querySelector('.rec-btn-text').textContent = 'Not supported';
        return;
      }

      var stream;
      try {
        stream = canvas.captureStream(30);
      } catch (err) {
        btn.querySelector('.rec-btn-text').textContent = 'Capture failed';
        return;
      }

      chunks = [];
      try {
        mediaRecorder = new MediaRecorder(stream, { mimeType: mime });
      } catch (err) {
        // Fallback without explicit mimeType
        mediaRecorder = new MediaRecorder(stream);
        mime = mediaRecorder.mimeType || 'video/webm';
      }

      mediaRecorder.ondataavailable = function (ev) {
        if (ev.data && ev.data.size > 0) chunks.push(ev.data);
      };

      mediaRecorder.onstop = function () {
        var blob = new Blob(chunks, { type: mime });
        var ext = getExtension(mime);
        var url = URL.createObjectURL(blob);
        var a = document.createElement('a');
        a.href = url;
        a.download = getFilename(container) + '.' + ext;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 5000);
        isRecording = false;
        btn.classList.remove('rec-btn--recording');
        btn.querySelector('.rec-btn-text').textContent = 'Record 10s';
      };

      mediaRecorder.start(100); // collect data every 100ms
      isRecording = true;
      btn.classList.add('rec-btn--recording');

      // Countdown in button text
      var remaining = 10;
      btn.querySelector('.rec-btn-text').textContent = remaining + 's...';
      timer = setInterval(function () {
        remaining--;
        if (remaining > 0) {
          btn.querySelector('.rec-btn-text').textContent = remaining + 's...';
        } else {
          clearInterval(timer);
          if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
          }
        }
      }, 1000);
    });
  }

  function initAll() {
    var selectors = ['.art-viz-inner', '.art-viz-secondary', '.inline-viz'];
    selectors.forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (container) {
        // Avoid double-attaching
        if (!container.querySelector('.rec-btn')) {
          attachRecorder(container);
        }
      });
    });
  }

  // Run after DOM + inline-viz.js have both had a chance to run
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      // Small delay so inline-viz.js finishes appending canvases
      setTimeout(initAll, 500);
    });
  } else {
    setTimeout(initAll, 500);
  }
})();
