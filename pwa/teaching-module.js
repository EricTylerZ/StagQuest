// Teaching Module - Category-agnostic framework for teaching virtues, gifts, fruits, etc.
// Reusable across Stellar Virtue and any other tools for Catholic moral formation.
//
// Question format:
//   { category: 'cardinal'|'gift'|'fruit'|..., topic: 'prudence', subtopic: 'memory',
//     level: 1, q: '...', answers: ['...'], correct: 0, explanation: '...' }
//
// Difficulty levels:
//   1 (Basic)        — Right vs. clearly wrong, foundational understanding
//   2 (Intermediate) — Distinguishing good from better, nuanced understanding
//   3 (Advanced)     — Subtle distinctions, cross-virtue connections, complex application
//
// The module handles:
//   - Question selection (prefer unmastered topics, avoid repeats, match difficulty level)
//   - Progress tracking per category/topic/subtopic
//   - Level-aware progressive mastery
//   - Category-agnostic design for any teaching content

// eslint-disable-next-line no-unused-vars
const TeachingModule = (function () {
  'use strict';

  // ===== Question Bank Registry =====
  const questionBanks = {};

  // ===== Category Metadata =====
  const categoryMeta = {};

  /**
   * Register a question bank for a category.
   * @param {string} category - e.g. 'cardinal', 'gift', 'fruit'
   * @param {Object} meta - { name, topics, masteryThreshold, levelsEnabled }
   * @param {Array} questions - Array of question objects
   */
  function registerCategory(category, meta, questions) {
    categoryMeta[category] = {
      name: meta.name || category,
      topics: meta.topics || {},
      masteryThreshold: meta.masteryThreshold || 2,
      levelsEnabled: meta.levelsEnabled !== false,
      maxLevel: meta.maxLevel || 3
    };
    questionBanks[category] = questions.map(function (q, i) {
      return Object.assign({}, q, {
        _bankIndex: i,
        category: category,
        level: q.level || 1
      });
    });
  }

  /**
   * Create a fresh progress tracker for all registered categories.
   * Progress is now per-level: { category: { topic: { subtopic: { level: N, correct: N } } } }
   * or for flat topics: { category: { topic: { level: N, correct: N } } }
   */
  function createProgressState() {
    var progress = {};
    Object.keys(categoryMeta).forEach(function (cat) {
      progress[cat] = {};
      var topics = categoryMeta[cat].topics;
      Object.keys(topics).forEach(function (topicId) {
        var topic = topics[topicId];
        if (topic.subtopics && topic.subtopics.length > 0) {
          progress[cat][topicId] = {};
          topic.subtopics.forEach(function (sub) {
            progress[cat][topicId][sub] = { level: 1, correct: 0 };
          });
        } else {
          progress[cat][topicId] = { level: 1, correct: 0 };
        }
      });
    });
    return progress;
  }

  /**
   * Get the progress object for a topic/subtopic.
   * Returns { level, correct } or a simple number for backward compat.
   */
  function getProgressObj(progressState, category, topic, subtopic) {
    if (!progressState[category]) return { level: 1, correct: 0 };
    var topicData = progressState[category][topic];
    if (!topicData) return { level: 1, correct: 0 };

    if (subtopic && typeof topicData === 'object' && !topicData.level) {
      // Nested subtopic structure
      var sub = topicData[subtopic];
      if (!sub) return { level: 1, correct: 0 };
      // Backward compat: if it's just a number, convert
      if (typeof sub === 'number') return { level: 1, correct: sub };
      return sub;
    }

    // Flat topic or backward compat
    if (typeof topicData === 'number') return { level: 1, correct: topicData };
    if (topicData.level !== undefined) return topicData;
    return { level: 1, correct: 0 };
  }

  /**
   * Get numeric progress value (backward compatible).
   */
  function getProgress(progressState, category, topic, subtopic) {
    var obj = getProgressObj(progressState, category, topic, subtopic);
    return obj.correct || 0;
  }

  /**
   * Get current mastery level for a topic/subtopic.
   */
  function getCurrentLevel(progressState, category, topic, subtopic) {
    var obj = getProgressObj(progressState, category, topic, subtopic);
    return obj.level || 1;
  }

  /**
   * Increment progress for a question's topic/subtopic.
   * Advances level when threshold is met.
   * @returns {{ correct: number, level: number, leveledUp: boolean }}
   */
  function incrementProgress(progressState, category, topic, subtopic) {
    var threshold = (categoryMeta[category] && categoryMeta[category].masteryThreshold) || 2;
    var maxLevel = (categoryMeta[category] && categoryMeta[category].maxLevel) || 3;

    // Navigate to the right place in progressState
    var target;
    if (subtopic && progressState[category] && progressState[category][topic] &&
        typeof progressState[category][topic] === 'object' && !progressState[category][topic].level) {
      if (!progressState[category][topic][subtopic]) {
        progressState[category][topic][subtopic] = { level: 1, correct: 0 };
      }
      target = progressState[category][topic][subtopic];
      // Backward compat
      if (typeof target === 'number') {
        progressState[category][topic][subtopic] = { level: 1, correct: target };
        target = progressState[category][topic][subtopic];
      }
    } else if (progressState[category] && progressState[category][topic] !== undefined) {
      if (typeof progressState[category][topic] === 'number') {
        progressState[category][topic] = { level: 1, correct: progressState[category][topic] };
      }
      if (!progressState[category][topic] || !progressState[category][topic].level) {
        progressState[category][topic] = { level: 1, correct: 0 };
      }
      target = progressState[category][topic];
    } else {
      return { correct: 0, level: 1, leveledUp: false };
    }

    target.correct = Math.min(threshold, (target.correct || 0) + 1);
    var leveledUp = false;

    // Level up when threshold met and not at max
    if (target.correct >= threshold && target.level < maxLevel) {
      target.level++;
      target.correct = 0;
      leveledUp = true;
    }

    return { correct: target.correct, level: target.level, leveledUp: leveledUp };
  }

  /**
   * Check if a topic/subtopic is mastered at its current level.
   */
  function isMastered(progressState, category, topic, subtopic) {
    var threshold = (categoryMeta[category] && categoryMeta[category].masteryThreshold) || 2;
    var obj = getProgressObj(progressState, category, topic, subtopic);
    return obj.correct >= threshold;
  }

  /**
   * Check if a topic/subtopic has reached maximum level.
   */
  function isFullyMastered(progressState, category, topic, subtopic) {
    var maxLevel = (categoryMeta[category] && categoryMeta[category].maxLevel) || 3;
    var threshold = (categoryMeta[category] && categoryMeta[category].masteryThreshold) || 2;
    var obj = getProgressObj(progressState, category, topic, subtopic);
    return obj.level >= maxLevel && obj.correct >= threshold;
  }

  /**
   * Check if an entire topic (all subtopics, all levels) is fully mastered.
   */
  function isTopicFullyMastered(progressState, category, topic) {
    if (!progressState[category] || !categoryMeta[category]) return false;
    var topicMeta = categoryMeta[category].topics[topic];
    if (!topicMeta) return false;

    if (topicMeta.subtopics && topicMeta.subtopics.length > 0) {
      return topicMeta.subtopics.every(function (sub) {
        return isFullyMastered(progressState, category, topic, sub);
      });
    }
    return isFullyMastered(progressState, category, topic);
  }

  /**
   * Check if an entire category is mastered.
   */
  function isCategoryMastered(progressState, category) {
    if (!categoryMeta[category]) return false;
    return Object.keys(categoryMeta[category].topics).every(function (topic) {
      return isTopicFullyMastered(progressState, category, topic);
    });
  }

  /**
   * Get a random question from a category (or all categories).
   * Prefers: current level > unmastered topics > unanswered questions.
   *
   * @param {Object} options
   * @param {string} [options.category] - Limit to a specific category
   * @param {Array} [options.answeredIndices] - Already-answered global IDs to deprioritize
   * @param {Object} [options.progressState] - Progress state for level/mastery-aware selection
   * @returns {{ question, globalId, category }} or null
   */
  function getRandomQuestion(options) {
    var opts = options || {};
    var categories = opts.category
      ? [opts.category]
      : Object.keys(questionBanks);

    // Build global pool
    var pool = [];
    categories.forEach(function (cat) {
      var bank = questionBanks[cat] || [];
      bank.forEach(function (q, i) {
        pool.push({ question: q, localIndex: i, category: cat, globalId: cat + ':' + i });
      });
    });

    if (pool.length === 0) return null;

    var answered = {};
    (opts.answeredIndices || []).forEach(function (id) { answered[String(id)] = true; });

    // Prefer unanswered
    var unanswered = pool.filter(function (p) { return !answered[p.globalId]; });
    var candidatePool = unanswered.length > 0 ? unanswered : pool;

    // Filter by current level and mastery
    if (opts.progressState) {
      // First: questions at the player's current level for unmastered topics
      var levelMatched = candidatePool.filter(function (p) {
        var q = p.question;
        var currentLvl = getCurrentLevel(opts.progressState, p.category, q.topic, q.subtopic);
        return q.level === currentLvl &&
               !isFullyMastered(opts.progressState, p.category, q.topic, q.subtopic);
      });
      if (levelMatched.length > 0) {
        var pick = levelMatched[Math.floor(Math.random() * levelMatched.length)];
        return { question: pick.question, globalId: pick.globalId, category: pick.category };
      }

      // Second: any unmastered question
      var unmastered = candidatePool.filter(function (p) {
        var q = p.question;
        return !isFullyMastered(opts.progressState, p.category, q.topic, q.subtopic);
      });
      if (unmastered.length > 0) {
        var pick2 = unmastered[Math.floor(Math.random() * unmastered.length)];
        return { question: pick2.question, globalId: pick2.globalId, category: pick2.category };
      }
    }

    var finalPick = candidatePool[Math.floor(Math.random() * candidatePool.length)];
    return { question: finalPick.question, globalId: finalPick.globalId, category: finalPick.category };
  }

  /**
   * Get display header for a question.
   */
  function getQuestionHeader(question) {
    var cat = categoryMeta[question.category];
    if (!cat) return question.topic || '';

    var topicMeta = cat.topics[question.topic];
    var topicName = topicMeta ? topicMeta.name : question.topic;

    if (question.subtopic && topicMeta && topicMeta.subtopicNames) {
      var subName = topicMeta.subtopicNames[question.subtopic] || question.subtopic;
      return topicName + ' \u2014 ' + subName;
    }

    return cat.name + ': ' + topicName;
  }

  /**
   * Get level label for display.
   */
  function getLevelLabel(level) {
    var labels = { 1: 'Basic', 2: 'Intermediate', 3: 'Advanced' };
    return labels[level] || ('Level ' + level);
  }

  /**
   * Get a summary of progress for a category.
   */
  function getCategoryProgress(progressState, category) {
    if (!categoryMeta[category]) return { mastered: 0, total: 0, topics: {} };
    var topics = categoryMeta[category].topics;
    var mastered = 0;
    var total = 0;
    var topicDetails = {};

    Object.keys(topics).forEach(function (topicId) {
      var fully = isTopicFullyMastered(progressState, category, topicId);
      if (fully) mastered++;
      total++;
      topicDetails[topicId] = {
        name: topics[topicId].name,
        mastered: fully,
        level: getCurrentLevel(progressState, category, topicId),
        progress: getProgress(progressState, category, topicId)
      };
    });

    return { mastered: mastered, total: total, topics: topicDetails };
  }

  /**
   * List all registered categories.
   */
  function getCategories() {
    return Object.keys(categoryMeta).map(function (cat) {
      return {
        id: cat,
        name: categoryMeta[cat].name,
        topicCount: Object.keys(categoryMeta[cat].topics).length,
        questionCount: (questionBanks[cat] || []).length
      };
    });
  }

  /**
   * Shuffle an array (Fisher-Yates).
   */
  function shuffle(arr) {
    var a = arr.slice();
    for (var i = a.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = a[i]; a[i] = a[j]; a[j] = tmp;
    }
    return a;
  }

  return {
    registerCategory: registerCategory,
    createProgressState: createProgressState,
    getProgress: getProgress,
    getCurrentLevel: getCurrentLevel,
    incrementProgress: incrementProgress,
    isMastered: isMastered,
    isFullyMastered: isFullyMastered,
    isTopicFullyMastered: isTopicFullyMastered,
    isCategoryMastered: isCategoryMastered,
    getRandomQuestion: getRandomQuestion,
    getQuestionHeader: getQuestionHeader,
    getLevelLabel: getLevelLabel,
    getCategoryProgress: getCategoryProgress,
    getCategories: getCategories,
    shuffle: shuffle
  };
})();
