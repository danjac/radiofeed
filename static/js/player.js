import { sendJSON, dispatch, formatDuration, percent } from './utils';

(function () {
  const Player = (options) => {
    const { mediaSrc, currentTime, episode, runImmediately } = options;

    const sessionKey = 'player-enabled';

    const defaults = {
      mediaSrc,
      currentTime: 0,
      duration: 0,
      isPlaying: false,
      isPaused: false,
      isLoaded: false,
      isWaiting: false,
      playbackRate: 1.0,
      counter: '00:00:00',
    };

    let timer;

    return {
      ...defaults,
      initialize() {
        this.$watch('duration', (value) => {
          this.updateProgressBar(value, this.currentTime);
        });
        this.$watch('currentTime', (value) => {
          this.updateProgressBar(this.duration, value);
        });
        this.openPlayer();
      },

      openPlayer() {
        this.stopPlayer();

        const dataTag = document.getElementById('player-metadata');

        if (dataTag && dataTag.textContent) {
          const metadata = JSON.parse(dataTag.textContent);
          if (metadata && 'mediaSession' in navigator) {
            if (Object.keys(metadata).length > 0) {
              navigator.mediaSession.metadata = new window.MediaMetadata(metadata);
            } else {
              navigator.mediaSession.metadata = null;
            }
          }
        }

        dispatch(this.$el, 'open-player', {
          episode,
        });
        dispatch(this.$el, 'remove-queue-item', {
          episode,
        });

        this.$nextTick(() => {
          this.$refs.audio.load();
        });
      },
      // audio events
      loaded() {
        this.$refs.audio.currentTime = currentTime;
        if (runImmediately || sessionStorage.getItem(sessionKey)) {
          this.$refs.audio
            .play()
            .then(() => {
              timer = setInterval(this.sendCurrentTimeUpdate.bind(this), 5000);
            })
            .catch((e) => {
              console.log(e);
              this.isPaused = true;
            });
        } else {
          this.isPaused = true;
        }
        this.duration = this.$refs.audio.duration;
        this.isLoaded = true;
      },
      timeUpdate() {
        this.currentTime = this.$refs.audio.currentTime;
      },
      resumed() {
        this.isPlaying = true;
        this.isPaused = false;
        this.isWaiting = false;
        sessionStorage.setItem(sessionKey, true);
      },
      paused() {
        this.isPlaying = false;
        this.isPaused = true;
        this.isWaiting = false;
        sessionStorage.removeItem(sessionKey);
      },

      waiting() {
        this.isWaiting = true;
      },

      active() {
        this.isWaiting = false;
      },

      ended() {
        this.stopPlayer();
        dispatch(this.$el, 'close-player');
        this.$refs.playNext.click();
      },

      shortcuts(event) {
        if (/^(INPUT|SELECT|TEXTAREA)$/.test(event.target.tagName)) {
          return;
        }

        const handlers = {
          '+': this.incrementPlaybackRate,
          '-': this.decrementPlaybackRate,
          ArrowLeft: this.skipBack,
          ArrowRight: this.skipForward,
          Space: this.togglePause,
          Delete: () => this.$refs.stop.click(),
        };

        const handler = handlers[event.code] || handlers[event.key];

        if (handler) {
          event.preventDefault();
          handler.bind(this)();
        }
      },

      incrementPlaybackRate() {
        this.changePlaybackRate(0.1);
      },
      decrementPlaybackRate() {
        this.changePlaybackRate(-0.1);
      },

      changePlaybackRate(increment) {
        const value = parseFloat(this.playbackRate);
        let newValue = value + increment;
        if (newValue > 2.0) {
          newValue = 2.0;
        } else if (newValue < 0.5) {
          newValue = 0.5;
        }
        this.$refs.audio.playbackRate = this.playbackRate = newValue;
      },

      skip({ clientX }) {
        const position = this.getProgressBarPosition(clientX);
        if (!isNaN(position) && position > -1) {
          this.skipTo(position);
        }
      },

      skipBack() {
        this.skipTo(this.$refs.audio.currentTime - 10);
      },

      skipForward() {
        this.skipTo(this.$refs.audio.currentTime + 10);
      },

      skipTo(position) {
        if (!isNaN(position) && !this.isPaused) {
          this.$refs.audio.currentTime = position;
        }
      },

      togglePause() {
        if (this.isPaused) {
          this.$refs.audio.play();
        } else {
          this.$refs.audio.pause();
        }
      },

      stopPlayer() {
        this.$refs.audio.pause();
        this.$refs.audio = null;
        if (timer) {
          clearInterval(timer);
        }
      },

      sendCurrentTimeUpdate() {
        if (!this.isPaused && this.currentTime) {
          sendJSON('/player/~timeupdate/', {
            currentTime: this.currentTime,
          });
        }
      },

      updateProgressBar(duration, currentTime) {
        if (this.$refs.indicator && this.$refs.progressBar) {
          this.counter = formatDuration(duration - currentTime);
          const pcComplete = percent(duration, currentTime);
          if (this.$refs.indicator) {
            this.$refs.indicator.style.left =
              this.getIndicatorPosition(pcComplete) + 'px';
          }
        }
      },

      getProgressBarPosition(clientX) {
        if (!isNaN(clientX)) {
          const { left } = this.$refs.progressBar.getBoundingClientRect();
          const width = this.$refs.progressBar.clientWidth;
          let position = clientX - left;
          return Math.ceil(this.duration * (position / width));
        } else {
          return -1;
        }
      },

      getIndicatorPosition(pcComplete) {
        const clientWidth = this.$refs.progressBar.clientWidth;
        let currentPosition, width;

        currentPosition = this.$refs.progressBar.getBoundingClientRect().left - 24;

        if (clientWidth === 0) {
          width = 0;
        } else {
          // min 1rem to accomodate indicator
          const minWidth = (16 / clientWidth) * 100;
          width = pcComplete > minWidth ? pcComplete : minWidth;
        }
        if (width) {
          currentPosition += clientWidth * (width / 100);
        }
        return currentPosition;
      },
    };
  };
  window.Player = Player;
})();