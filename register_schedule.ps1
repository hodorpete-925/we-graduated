# register_schedule.ps1 - We Graduated jobs in Windows Task Scheduler (copied from I Yearn's).
# Run once, in PowerShell, from this folder:   powershell -ExecutionPolicy Bypass -File register_schedule.ps1
# Re-running replaces the tasks. Remove with:  Unregister-ScheduledTask -TaskName "WeGrad*" -Confirm:$false
#
#   WeGrad daily refresh : every day 7:20 AM  -> refresh.py "Scheduled morning refresh"
#   WeGrad game scores   : hourly in game windows -> live_scores.py (pushes scores.json only)
#       Thu 8 PM-midnight, Sun noon-midnight, Mon 8 PM-midnight (local time)
#
# Same settings as I Yearn: runs only while the PC is awake (a missed run starts when it
# wakes), runs on battery, and times are stored as plain local time so daylight saving
# doesn't shift them. 7:20 so it doesn't collide with I Yearn's 7:00 job.

$repo = Split-Path -Parent $MyInvocation.MyCommand.Path
$py   = (Resolve-Path (Join-Path $repo "..\Fantasy Football API Work\venv\Scripts\pythonw.exe")).Path
$set  = New-ScheduledTaskSettingsSet -StartWhenAvailable -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
          -ExecutionTimeLimit (New-TimeSpan -Minutes 30) -MultipleInstances IgnoreNew

function LocalTime($trigger, $at) {
  $trigger.StartBoundary = (Get-Date $at).ToString("yyyy-MM-dd'T'HH:mm:ss")
  return $trigger
}

$daily = New-ScheduledTaskAction -Execute $py -Argument 'refresh.py "Scheduled morning refresh"' -WorkingDirectory $repo
$dailyTrigger = LocalTime (New-ScheduledTaskTrigger -Daily -At 7:20AM) "7:20AM"
Register-ScheduledTask -TaskName "WeGrad daily refresh" -Action $daily -Settings $set -Force -Trigger $dailyTrigger | Out-Null

$scores = New-ScheduledTaskAction -Execute $py -Argument 'live_scores.py' -WorkingDirectory $repo
function HourlyWindow($day, $start, $hours) {
  $t = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $day -At $start
  $r = New-ScheduledTaskTrigger -Once -At $start -RepetitionInterval (New-TimeSpan -Hours 1) -RepetitionDuration (New-TimeSpan -Hours $hours)
  $t.Repetition = $r.Repetition
  return (LocalTime $t $start)
}
$triggers = @(
  (HourlyWindow Thursday "8:10PM" 4),
  (HourlyWindow Sunday   "12:10PM" 12),
  (HourlyWindow Monday   "8:10PM" 4)
)
Register-ScheduledTask -TaskName "WeGrad game scores" -Action $scores -Settings $set -Trigger $triggers -Force | Out-Null

Get-ScheduledTask -TaskName "WeGrad*" | Get-ScheduledTaskInfo | Format-Table TaskName, NextRunTime
