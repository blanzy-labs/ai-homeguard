import type { QuestionnaireSection, QuestionnaireSubmission } from "../api/client";

type QuestionnaireScreenProps = {
  sections: QuestionnaireSection[];
  answers: Record<string, string>;
  onAnswerChange: (questionId: string, value: string) => void;
  onSubmit: (submission: QuestionnaireSubmission) => void;
  isSubmitting: boolean;
  kicker?: string;
  heading?: string;
  description?: string;
  submitLabel?: string;
  submittingLabel?: string;
  skipLabel?: string;
  onSkip?: () => void;
};

export function QuestionnaireScreen({
  sections,
  answers,
  onAnswerChange,
  onSubmit,
  isSubmitting,
  kicker = "Questionnaire",
  heading = "Home Security Checklist",
  description = "Answer what you can. Optional questions can be skipped, and no passwords, addresses, account names, device identifiers, or Wi-Fi join codes are requested.",
  submitLabel = "View Questionnaire Results",
  submittingLabel = "Building Report",
  skipLabel = "Skip for Now",
  onSkip,
}: QuestionnaireScreenProps) {
  const questions = sections.flatMap((section) => section.questions);
  const answeredCount = questions.filter((question) => answers[question.id]).length;
  const requiredAnswered = questions
    .filter((question) => question.required)
    .every((question) => Boolean(answers[question.id]));

  function buildSubmission(): QuestionnaireSubmission {
    return {
      mode: "questionnaire",
      answers: questions.map((question) => ({
        question_id: question.id,
        value: answers[question.id] ?? null,
        skipped: !answers[question.id],
      })),
    };
  }

  return (
    <section className="questionnaire-panel" aria-labelledby="questionnaire-heading">
      <div className="flow-heading">
        <p className="section-kicker">{kicker}</p>
        <h2 id="questionnaire-heading">{heading}</h2>
        <p className="muted">{description}</p>
      </div>

      <div className="progress-strip" aria-label="Questionnaire progress">
        <span>
          {answeredCount} of {questions.length} answered
        </span>
        <strong>{Math.round((answeredCount / questions.length) * 100)}%</strong>
      </div>

      <div className="questionnaire-sections">
        {sections.map((section) => (
          <section className="question-section" key={section.id} aria-labelledby={`${section.id}-heading`}>
            <div>
              <h3 id={`${section.id}-heading`}>{section.title}</h3>
              <p>{section.description}</p>
            </div>

            {section.questions.map((question) => (
              <fieldset className="question-card" key={question.id}>
                <legend>
                  {question.prompt}
                  {question.required ? <span>Required</span> : null}
                </legend>
                {question.help_text ? <p>{question.help_text}</p> : null}

                <div className="answer-options">
                  {question.options.map((option) => (
                    <label key={`${question.id}-${option.value}`}>
                      <input
                        type="radio"
                        name={question.id}
                        value={option.value}
                        checked={answers[question.id] === option.value}
                        onChange={() => onAnswerChange(question.id, option.value)}
                      />
                      <span>{option.label}</span>
                    </label>
                  ))}
                </div>
              </fieldset>
            ))}
          </section>
        ))}
      </div>

      <div className="questionnaire-actions">
        <p className="muted">
          These answers are used only to create questionnaire-based findings in this browser session.
        </p>
        {onSkip ? (
          <button className="secondary-button" type="button" disabled={isSubmitting} onClick={onSkip}>
            {skipLabel}
          </button>
        ) : null}
        <button
          className="primary-button"
          type="button"
          disabled={!requiredAnswered || isSubmitting}
          onClick={() => onSubmit(buildSubmission())}
        >
          {isSubmitting ? submittingLabel : submitLabel}
        </button>
      </div>
    </section>
  );
}
