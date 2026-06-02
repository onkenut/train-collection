interface PreviewPaneProps {
  content: string
}

export function PreviewPane({ content }: PreviewPaneProps) {
  return (
    <div
      className="milkdown h-full overflow-y-auto p-6"
    >
      <div
        className="prose max-w-none"
        dangerouslySetInnerHTML={{ __html: simpleMarkdownRender(content) }}
      />
    </div>
  )
}

function simpleMarkdownRender(md: string): string {
  let html = md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/^- \[x\] (.+)$/gm, '<li><input type="checkbox" checked disabled /> $1</li>')
    .replace(/^- \[ \] (.+)$/gm, '<li><input type="checkbox" disabled /> $1</li>')
    .replace(/^- (.+)$/gm, '<li>$1</li>')
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    .replace(/^---$/gm, '<hr/>')
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')

  html = html.replace(/\n\n/g, '</p><p>')
  html = '<p>' + html + '</p>'
  html = html.replace(/<p><(h[1-3]|blockquote|hr|li|ul|ol)/g, '<$1')
  html = html.replace(/<\/(h[1-3]|blockquote|li|ul|ol)><\/p>/g, '</$1>')
  html = html.replace(/<p><hr\/><\/p>/g, '<hr/>')

  return html
}
