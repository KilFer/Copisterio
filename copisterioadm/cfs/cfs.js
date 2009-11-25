new Ajax.PeriodicalUpdater('count', '/count/', {
  method: 'get',
  frequency: 3,
  decay: 2,
});

