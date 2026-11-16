import Markdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

/** Inline markdown for short fields (backticks, bold, italics) without wrapping paragraphs. */
export function Inline({ children }: { children: string }) {
  return <Markdown remarkPlugins={[remarkGfm]} components={{
    p: ({ children }) => <>{children}</>,
    a: ({ href, children }) => <a href={href} target="_blank" rel="noreferrer">{children}</a>,
  }}>{children}</Markdown>
}

/** Renders the markdown our own content modules produce. Raw HTML is not rendered (react-markdown escapes it). */
export default function Md({ children }: { children: string }) {
  return (
    <div className="md">
      <Markdown
        remarkPlugins={[remarkGfm]}
        components={{ table: ({ children }) => <div className="scroll"><table>{children}</table></div> }}
      >
        {children}
      </Markdown>
    </div>
  )
}
