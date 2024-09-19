from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.monitors.mixins import ValidationMonitorMixin


@monitors.name('Custom item validation monitor')
@monitors.description('Custom validation of the extracted item fields.')
class CustomItemValidationMonitor(Monitor, ValidationMonitorMixin):
    @monitors.name('Required fields')
    @monitors.description("Validates that all the item required fields are present.")
    def test_required_fields(self):
        self.check_missing_required_fields()

    @monitors.name('Check field validation')
    @monitors.description("Validates that all the fields are valid")
    def test_fields_errors(self):
        self.check_fields_errors()


class SpiderCloseMonitorSuite(MonitorSuite):
    monitors = [
        CustomItemValidationMonitor,
    ]
