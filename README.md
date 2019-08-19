# advert_notifier

Script created to monitor new adverts in {olx,gumtree} and send SMS/Email notification. May be helpful if you're looking for good deals ;)

The best way to run it is though cron, eg.

`*/15 * * * * python3 <path_to_script>/crawler.py >> <path_to_script>/log >/dev/null 2>&1`
