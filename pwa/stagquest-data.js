// StagQuest - Virtue Deck Data, Teaching Questions & Prayer Content
// 9-day novena to fight human trafficking through personal discipline

const STAGQUEST_DATA = (() => {
  'use strict';

  // === 7 Canonical Hours ===
  const HOURS = [
    { id: 'lauds', name: 'Lauds', label: 'Morning Prayer', hour: 6,
      prayer: 'Lord, as this new day dawns, I offer my vigilance against temptation as a prayer for the 40 million enslaved. Strengthen my resolve. Amen.' },
    { id: 'prime', name: 'Prime', label: 'Early Morning', hour: 7,
      prayer: 'Father, at this hour of resolve, arm me against the $150B industry that exploits the innocent. I commit to purity today. Amen.' },
    { id: 'terce', name: 'Terce', label: 'Mid-Morning (9am)', hour: 9,
      prayer: 'Holy Spirit, at the hour of Christ\'s trial and Your descent, give me strength to fight the temptations that rewire my mind. Shield the 2.5 million trafficked this year. Amen.' },
    { id: 'sext', name: 'Sext', label: 'Midday (Noon)', hour: 12,
      prayer: 'Lord Jesus, at the hour of Your crucifixion, I remember that 76% of trafficking victims are children. Guard my eyes; let me choose life. Amen.' },
    { id: 'none', name: 'None', label: 'Afternoon (3pm)', hour: 15,
      prayer: 'Jesus, at the hour of Your death, I pray to sever every chain of addiction. Each clean day cuts traffickers\' revenue. Give me the grace to endure. Amen.' },
    { id: 'vespers', name: 'Vespers', label: 'Evening', hour: 17,
      prayer: 'Lord, as evening falls, I reflect on today\'s victories and failures. Renew my will. Guard my heart against the evil that preys on weakness. Amen.' },
    { id: 'compline', name: 'Compline', label: 'Night Prayer', hour: 21,
      prayer: 'Into Your hands, O Lord, I commend this day. Every "no" to temptation saves lives. Seal this day in peace and rest. Amen.' }
  ];

  // === 22 Virtue Cards (from the card game) ===
  const VIRTUE_CARDS = [
    { hour: 'lauds', title: 'Lauds Prayer', text: '40M are trafficked\u2014addiction fuels this. Pray to break free today.', fact: 'Lauds (dawn) praises the new day.' },
    { hour: 'prime', title: 'Prime Resolve', text: 'Porn\'s a $150B industry exploiting kids. Commit to purity now.', fact: 'Prime (early morning) starts the day\'s work.' },
    { hour: 'terce', title: 'Terce Strength', text: 'Temptation rewires your brain\u2014fight it to reclaim your mind.', fact: 'Terce (mid-morning, 9am) marks Christ\'s trial.' },
    { hour: 'sext', title: 'Sext Reflection', text: '76% of trafficking victims are under 18. Reflect on who you protect.', fact: 'Sext (noon) recalls Christ\'s crucifixion.' },
    { hour: 'none', title: 'None Cut', text: 'Porn\'s progressive\u2014each view deepens the trap. Pray to sever it.', fact: 'None (mid-afternoon, 3pm) recalls Christ\'s death.' },
    { hour: 'vespers', title: 'Vespers Stand', text: '9,000 illicit massage parlors thrive on demand. Take a stand to end this exploitation.', fact: 'Vespers (evening) reflects on the day.' },
    { hour: 'compline', title: 'Compline Rest', text: 'Addiction funds evil\u2014every \'no\' saves lives. Rest in this victory.', fact: 'Compline (night) seals the day in peace.' },
    { hour: 'lauds', title: 'Lauds Hope', text: 'A child sold every 2 min\u2014your virtue restores hope. Plan one good deed.' },
    { hour: 'prime', title: 'Prime Focus', text: 'Dopamine spikes blind you\u2014resist to heal your soul.' },
    { hour: 'terce', title: 'Terce Shield', text: '2.5M trafficked yearly\u2014your fight shields them. Pray for strength.', fact: 'Terce also recalls the Spirit\'s descent.' },
    { hour: 'sext', title: 'Sext Vision', text: 'Your eyes choose life or death\u2014guard them to lead your family.' },
    { hour: 'none', title: 'None Break', text: 'Porn drives 42% of family trafficking. Break the cycle now.' },
    { hour: 'vespers', title: 'Vespers Renewal', text: 'Habits form in weeks\u2014renew your will to defy lust\'s pull.' },
    { hour: 'compline', title: 'Compline Peace', text: 'Each clean day cuts traffickers\' cash. Note your progress.' },
    { hour: 'lauds', title: 'Lauds Rally', text: '14M new victims annually\u2014rally your spirit to end this.' },
    { hour: 'prime', title: 'Prime Triumph', text: 'Virtue builds a shield\u2014help another resist temptation today.' },
    { hour: 'terce', title: 'Terce Legacy', text: 'Your vigilance leaves a legacy\u2014pray to endure.' },
    { hour: 'sext', title: 'Sext Growth', text: 'Each win cuts evil\'s cash\u2014grow strong for your family.' },
    { hour: 'none', title: 'None Victory', text: 'Resist today to weaken exploitation\'s grip. Celebrate the win.' },
    { hour: 'vespers', title: 'Vespers Guard', text: 'Guard your heart\u2014evil preys on weakness. Stand firm.' },
    { hour: 'compline', title: 'Compline Joy', text: 'A pure day protects the vulnerable. Rest in joy.' },
    { hour: 'lauds', title: 'Lauds Rise', text: 'Rise each day to fight for the exploited\u2014start with prayer.' }
  ];

  // === Teaching Questions ===
  const QUESTIONS = [
    // TRAFFICKING AWARENESS - Level 1
    { category: 'stagquest', topic: 'trafficking', subtopic: 'awareness',
      question: 'Approximately how many people are currently victims of human trafficking worldwide?',
      answers: ['40 million', '1 million', '100,000', '500 million'],
      correct: 0, level: 1 },
    { category: 'stagquest', topic: 'trafficking', subtopic: 'awareness',
      question: 'What percentage of trafficking victims are under 18?',
      answers: ['76%', '10%', '50%', '25%'],
      correct: 0, level: 1 },
    { category: 'stagquest', topic: 'trafficking', subtopic: 'prevention',
      question: 'How does personal addiction fuel the trafficking industry?',
      answers: ['Demand for exploitative content creates a market that traffickers supply', 'It doesn\'t have any connection', 'Only drug addiction is connected', 'Trafficking is only about labor'],
      correct: 0, level: 1 },
    // TRAFFICKING - Level 2
    { category: 'stagquest', topic: 'trafficking', subtopic: 'awareness',
      question: 'What percentage of family trafficking cases involve pornography as a factor?',
      answers: ['42%', '5%', '90%', '15%'],
      correct: 0, level: 2 },
    { category: 'stagquest', topic: 'trafficking', subtopic: 'prevention',
      question: 'How does the $150 billion pornography industry relate to trafficking?',
      answers: ['It normalizes exploitation and creates demand that traffickers supply', 'They are completely separate industries', 'The industry prevents trafficking', 'Only illegal content is connected'],
      correct: 0, level: 2 },
    { category: 'stagquest', topic: 'trafficking', subtopic: 'action',
      question: 'Why does every day of personal purity directly weaken trafficking?',
      answers: ['Reduced demand means less profit for traffickers', 'It doesn\'t really help', 'Only policy changes matter', 'Personal choices are too small to matter'],
      correct: 0, level: 2 },
    // TRAFFICKING - Level 3
    { category: 'stagquest', topic: 'trafficking', subtopic: 'awareness',
      question: 'How does the progressive nature of addiction escalate into trafficking demand?',
      answers: ['Desensitization drives consumers to seek increasingly extreme content, eventually fueling live exploitation', 'Addiction stays at the same level', 'Only criminal minds drive trafficking', 'Technology prevents escalation'],
      correct: 0, level: 3 },

    // PERSONAL VIRTUE - Level 1
    { category: 'stagquest', topic: 'virtue', subtopic: 'purity',
      question: 'What is purity of heart?',
      answers: ['Guarding your mind and senses to see the dignity in every person', 'Never having a bad thought', 'Being physically clean', 'Avoiding all media'],
      correct: 0, level: 1 },
    { category: 'stagquest', topic: 'virtue', subtopic: 'discipline',
      question: 'Why is daily discipline important in fighting temptation?',
      answers: ['Habits of virtue grow stronger with consistent practice', 'One big effort is enough', 'Discipline doesn\'t matter if your heart is good', 'Only monks need daily discipline'],
      correct: 0, level: 1 },
    { category: 'stagquest', topic: 'virtue', subtopic: 'courage',
      question: 'What role does courage play in the fight against personal sin?',
      answers: ['It takes bravery to resist what is easy and choose what is right', 'Courage is only for physical battles', 'Spiritual battles don\'t require courage', 'Avoiding temptation doesn\'t take courage'],
      correct: 0, level: 1 },
    // VIRTUE - Level 2
    { category: 'stagquest', topic: 'virtue', subtopic: 'purity',
      question: 'How does guarding your eyes protect your family?',
      answers: ['What we consume shapes who we become\u2014purity of vision builds the capacity to love selflessly', 'It only affects the individual', 'Eyes have nothing to do with family life', 'Protection of family is only about physical safety'],
      correct: 0, level: 2 },
    { category: 'stagquest', topic: 'virtue', subtopic: 'discipline',
      question: 'How does the brain\'s reward system relate to virtue?',
      answers: ['Dopamine reinforces habits\u2014virtue redirects this system toward lasting goods', 'Brain chemistry is irrelevant to morality', 'Virtue is purely spiritual', 'Science and faith are separate'],
      correct: 0, level: 2 },
    { category: 'stagquest', topic: 'virtue', subtopic: 'courage',
      question: 'Why does helping another person resist temptation require courage?',
      answers: ['It means being vulnerable, risking rejection, and speaking difficult truths in love', 'It doesn\'t require any courage', 'Others\' temptations aren\'t our business', 'Only professionals should help with this'],
      correct: 0, level: 2 },
    // VIRTUE - Level 3
    { category: 'stagquest', topic: 'virtue', subtopic: 'purity',
      question: 'How does the Thomistic understanding of temperance inform the fight against addiction?',
      answers: ['Temperance orders the passions under reason\u2014addiction is the surrender of reason to disordered appetite', 'Temperance only applies to food and drink', 'Thomistic virtue is outdated', 'Addiction is a disease, not a virtue problem'],
      correct: 0, level: 3 },

    // PRAYER LIFE - Level 1
    { category: 'stagquest', topic: 'prayer', subtopic: 'hours',
      question: 'What are the Liturgy of the Hours?',
      answers: ['A cycle of daily prayers at set times, sanctifying each part of the day', 'A medieval tradition no longer practiced', 'Prayers only for priests and monks', 'A single prayer said once per day'],
      correct: 0, level: 1 },
    { category: 'stagquest', topic: 'prayer', subtopic: 'intention',
      question: 'How does praying for trafficking victims help?',
      answers: ['Prayer brings God\'s grace to bear on the situation and strengthens the one who prays to act', 'It doesn\'t actually help anyone', 'Only action matters, not prayer', 'God already knows, so prayer is unnecessary'],
      correct: 0, level: 1 },
    { category: 'stagquest', topic: 'prayer', subtopic: 'perseverance',
      question: 'Why is a 9-day novena effective for building spiritual strength?',
      answers: ['Sustained prayer over 9 days builds habit, deepens trust, and opens the heart to grace', '9 is a magic number', 'One prayer is always enough', 'Novenas are superstitious'],
      correct: 0, level: 1 },
    // PRAYER - Level 2
    { category: 'stagquest', topic: 'prayer', subtopic: 'hours',
      question: 'What is the significance of praying at the 3pm hour (None)?',
      answers: ['It commemorates the hour of Christ\'s death\u2014the ultimate act of self-sacrifice', 'It\'s just a convenient time', '3pm has no special meaning', 'It\'s the hottest part of the day, so we pray for comfort'],
      correct: 0, level: 2 },
    { category: 'stagquest', topic: 'prayer', subtopic: 'intention',
      question: 'How does offering your daily discipline as a prayer differ from mere self-improvement?',
      answers: ['It transforms personal effort into an act of love for others\u2014your "no" becomes a prayer for the enslaved', 'There is no difference', 'Self-improvement is better than prayer', 'Intentions don\'t change actions'],
      correct: 0, level: 2 },
    // PRAYER - Level 3
    { category: 'stagquest', topic: 'prayer', subtopic: 'perseverance',
      question: 'How does the Catholic understanding of redemptive suffering apply to the daily struggle against temptation?',
      answers: ['Our suffering united with Christ\'s becomes salvific\u2014each battle against temptation participates in His redemptive work', 'Suffering has no redemptive value', 'Only Christ\'s suffering matters', 'This theology encourages unnecessary pain'],
      correct: 0, level: 3 },

    // PROTECTION - Level 1
    { category: 'stagquest', topic: 'protection', subtopic: 'family',
      question: 'How does personal purity protect your family?',
      answers: ['It builds a shield of trust and integrity that keeps the family safe from exploitation', 'Personal choices don\'t affect families', 'Only physical protection matters', 'Privacy means family doesn\'t know'],
      correct: 0, level: 1 },
    { category: 'stagquest', topic: 'protection', subtopic: 'digital',
      question: 'Why is digital safety important in the fight against trafficking?',
      answers: ['The internet is a primary tool for traffickers to recruit and exploit victims', 'The internet is always safe', 'Trafficking only happens in person', 'Digital safety is just about passwords'],
      correct: 0, level: 1 },
    // PROTECTION - Level 2
    { category: 'stagquest', topic: 'protection', subtopic: 'community',
      question: 'How does a community of accountability help individuals fight addiction?',
      answers: ['Shared commitment, transparency, and mutual support multiply the strength of each person\'s resolve', 'People should fight alone', 'Sharing struggles is embarrassing and unhelpful', 'Only professional therapy works'],
      correct: 0, level: 2 },
    { category: 'stagquest', topic: 'protection', subtopic: 'family',
      question: 'What is the connection between a father\'s purity and his children\'s safety?',
      answers: ['A father\'s integrity shapes the family culture\u2014purity models the dignity every child deserves', 'There is no connection', 'Only mothers protect children', 'Safety is about locks and rules, not virtue'],
      correct: 0, level: 2 },
  ];

  function registerQuestions() {
    if (typeof TeachingModule === 'undefined') return;
    TeachingModule.registerCategory('stagquest', {
      name: 'StagQuest Novena',
      topics: {
        trafficking: { name: 'Human Trafficking', subtopics: { awareness: 'Awareness', prevention: 'Prevention', action: 'Action' } },
        virtue: { name: 'Personal Virtue', subtopics: { purity: 'Purity', discipline: 'Discipline', courage: 'Courage' } },
        prayer: { name: 'Prayer Life', subtopics: { hours: 'Hours', intention: 'Intention', perseverance: 'Perseverance' } },
        protection: { name: 'Protection', subtopics: { family: 'Family', community: 'Community', digital: 'Digital' } }
      },
      masteryThreshold: 2,
      maxLevel: 3
    }, QUESTIONS);
  }

  function getCurrentHour() {
    const h = new Date().getHours();
    // Find the current or most recent canonical hour
    const sorted = [...HOURS].sort((a, b) => b.hour - a.hour);
    return sorted.find(hr => h >= hr.hour) || HOURS[0];
  }

  function getCardForHour(hourId) {
    const cards = VIRTUE_CARDS.filter(c => c.hour === hourId);
    return cards[Math.floor(Math.random() * cards.length)];
  }

  return { HOURS, VIRTUE_CARDS, QUESTIONS, registerQuestions, getCurrentHour, getCardForHour };
})();
