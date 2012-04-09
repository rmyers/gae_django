from debug_toolbar.panels import DebugPanel
from google.appengine.ext.appstats.recording import start_recording,\
    end_recording, recorder_proxy
import logging

class AppStatsPanel(DebugPanel):
    """
    Appstats Panel for django-debug-toolbar
    """
    
    name = 'AppStats'
    template = 'debug_toolbar/panels/appstats.html'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(AppStatsPanel, self).__init__(*args, **kwargs)
        self._start = 0
        self._duration = 0
        self._overhead = 0
        self._num_traces = 0
        self._rpc_time = 0
        
    def nav_title(self):
        """Title showing in toolbar"""
        return self.name

    def nav_subtitle(self):
        """Subtitle showing until title in toolbar"""
        return "%d rpc calls in %.2fms" % (self._num_traces, self._duration)

    def title(self):
        """Title showing in panel"""
        return 'Appstats for View '

    def url(self):
        return ''

    def record_appstats(self, title, stats):
        """Callback that appengine appstats uses to """
        self._start = stats.get('start', 0)
        self._duration = stats.get('duration', 0)
        self._overhead = stats.get('overhead', 0)
        self._num_traces = len(stats.get('traces', []))
        for t in stats.get('traces', []):
            self._rpc_time += t['duration']
        stats['rpc_time'] = self._rpc_time
        self.record_stats(stats)

    def process_request(self, request):
        """Called by Django before deciding which view to execute."""
        start_recording()

    def process_response(self, request, response):
        """Called by Django just before returning a response."""
        #rec = recorder_proxy.get_for_current_request()
        #self.record_appstats(rec)
        end_recording(response.status_code, self.record_appstats)
        return response