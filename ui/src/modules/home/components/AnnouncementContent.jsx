function renderParagraphs(paragraphs, keyPrefix) {
  if (!Array.isArray(paragraphs)) {
    return null;
  }

  return paragraphs.map((text, index) => (
    <p key={`${keyPrefix}-paragraph-${index}`}>{text}</p>
  ));
}

function AnnouncementContent({ announcement }) {
  if (!announcement) {
    return null;
  }

  const { title, videoPlatforms = [], summary = [], sections = [], tasks = [] } = announcement;

  return (
    <div className="announcement-content">
      {title && (
        <h3 className="announcement-title" aria-label={title}>
          {title}
        </h3>
      )}
      {videoPlatforms.length > 0 && (
        <p className="announcement-highlight">{`Tutorial video: ${videoPlatforms.join(' / ')}`}</p>
      )}
      {renderParagraphs(summary, 'summary')}
      {sections.map((section) => (
        <section key={section.heading} className="announcement-section">
          {section.heading && <h4>{section.heading}</h4>}
          {renderParagraphs(section.paragraphs, section.heading || 'section')}
          {Array.isArray(section.list) && section.list.length > 0 && (
            <ul>
              {section.list.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
          {section.codeExample && (
            <pre className="announcement-code">
              <code>{section.codeExample}</code>
            </pre>
          )}
          {section.closing && <p>{section.closing}</p>}
        </section>
      ))}
      {tasks.length > 0 && (
        <div className="announcement-tasks">
          <h4>Identifica las tareas</h4>
          <ul>
            {tasks.map((task) => (
              <li key={task}>{task}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default AnnouncementContent;
