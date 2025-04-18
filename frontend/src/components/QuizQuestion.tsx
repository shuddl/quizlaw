import React, { useState } from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import { QuizQuestion as QuizQuestionType, AnswerCheck } from '@/services/api';
import { useAuth } from '@/context/AuthContext';

interface QuizQuestionProps {
  question: QuizQuestionType;
  onAnswer: (answer: string) => Promise<AnswerCheck>;
  onNext: () => void;
}

const QuizQuestion: React.FC<QuizQuestionProps> = ({ question, onAnswer, onNext }) => {
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [answerResult, setAnswerResult] = useState<AnswerCheck | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { isPremium } = useAuth();

  const handleAnswerClick = async (answer: string) => {
    if (selectedAnswer || isSubmitting) return;
    
    setSelectedAnswer(answer);
    setIsSubmitting(true);
    
    try {
      const result = await onAnswer(answer);
      setAnswerResult(result);
    } catch (error) {
      console.error('Error checking answer:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getOptionClass = (option: string) => {
    if (!selectedAnswer || !answerResult) {
      return 'border-gray-300 hover:border-gray-400';
    }
    
    if (answerResult.correct_answer === option) {
      return 'correct-answer';
    }
    
    if (selectedAnswer === option && !answerResult.is_correct) {
      return 'incorrect-answer';
    }
    
    return 'border-gray-300 opacity-70';
  };

  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <h3 className="text-xl font-semibold mb-4">{question.question_text}</h3>
      
      <div className="space-y-3 mb-6">
        {Object.entries(question.options).map(([key, value]) => (
          <button
            key={key}
            className={clsx(
              'w-full text-left p-4 border rounded-lg transition-all',
              getOptionClass(key),
              selectedAnswer ? 'cursor-default' : 'hover:shadow-md'
            )}
            onClick={() => handleAnswerClick(key)}
            disabled={!!selectedAnswer}
          >
            <span className="font-bold mr-2">{key}.</span> {value}
          </button>
        ))}
      </div>
      
      {answerResult && (
        <motion.div
          className="mt-4"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          transition={{ duration: 0.3 }}
        >
          <div className={clsx(
            'p-4 border rounded-lg',
            answerResult.is_correct ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
          )}>
            <p className="font-bold mb-2">
              {answerResult.is_correct ? '✓ Correct!' : '✗ Incorrect'}
            </p>
            
            {!answerResult.is_correct && (
              <p className="mb-2">
                The correct answer is: <strong>{answerResult.correct_answer}</strong>
              </p>
            )}
            
            {answerResult.explanation ? (
              <div className="mt-2">
                <h4 className="font-semibold mb-1">Explanation:</h4>
                <p>{answerResult.explanation}</p>
              </div>
            ) : isPremium ? (
              <p className="italic text-gray-600">No explanation available.</p>
            ) : (
              <div className="border border-dashed border-gray-300 rounded-lg p-3 mt-3 bg-gray-50">
                <p className="text-center text-gray-500">
                  <span className="block font-semibold mb-1">Premium Feature</span>
                  Upgrade to see explanations for all answers
                </p>
                <button className="btn-primary w-full mt-2 text-center">
                  Upgrade to Premium
                </button>
              </div>
            )}
          </div>
          
          <button
            className="btn-primary w-full mt-4"
            onClick={onNext}
          >
            Next Question
          </button>
        </motion.div>
      )}
      
      {question.source_url && (
        <div className="mt-4 text-sm text-gray-500">
          <a
            href={question.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="underline hover:text-primary"
          >
            View Source
          </a>
        </div>
      )}
    </motion.div>
  );
};

export default QuizQuestion;