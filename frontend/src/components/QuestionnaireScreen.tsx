import type { QuestionnaireSection, QuestionnaireSubmission } from "../api/client";

type QuestionnaireScreenProps = {
  sections: QuestionnaireSection[];
  answers: Record<string, string>;
  onAnswerChange: (questionId: string, value: string) => void;
  onSubmit: (submission: QuestionnaireSubmission) => void;
  isSubmitting: boolean;
};

export function QuestionnaireScreen({
  sections,
  answers,
  onAnswerChange,
  onSubmit,
  isSubmitting,
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
        <p className="section-kicker">Questionnaire</p>
        <h2 id="questionnaire-heading">Home Security Checklist</h2>
        <p className="muted">
          Answer what you can. Optional questions can be skipped, and no passwords, addresses,
          account names, device identifiers, or Wi-Fi join codes are requested.
        </p>
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
        <button
          className="primary-button"
          type="button"
          disabled={!requiredAnswered || isSubmitting}
          onClick={() => onSubmit(buildSubmission())}
        >
          {isSubmitting ? "Building Report" : "View Questionnaire Results"}
        </button>
      </div>
    </section>
  );
}
