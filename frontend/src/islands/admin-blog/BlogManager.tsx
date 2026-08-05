import AddBlogForm from './AddBlogForm'
import BlogPostCard from './BlogPostCard'
import Skeleton from '../../lib/Skeleton'
import { useCrudList } from '../../lib/useCrudList'
import type { BlogPost } from './schema'

const ENDPOINT = '/api/admin-hub/blog/'

export default function BlogManager() {
  const { items: posts, loadState, add, update, remove } = useCrudList<BlogPost>(ENDPOINT)

  if (loadState === 'loading') {
    return (
      <div className="blog-grid" aria-hidden="true">
        {Array.from({ length: 3 }).map((_, i) => (
          <div className="blog-card" key={i}>
            <Skeleton style={{ width: '100%', aspectRatio: '16 / 9' }} />
            <div className="blog-card__body">
              <Skeleton className="skeleton-text" style={{ width: '70%', height: 20, marginBottom: 12 }} />
              <Skeleton className="skeleton-text" style={{ width: '100%' }} />
              <Skeleton className="skeleton-text" style={{ width: '85%' }} />
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (loadState === 'error') {
    return <p className="form-note">Couldn&apos;t load blog posts. Reload the page and try again.</p>
  }

  return (
    <>
      <AddBlogForm onAdded={add} />
      {posts.length === 0 ? (
        <p className="section__sub">No blog posts yet.</p>
      ) : (
        <div className="blog-grid">
          {posts.map((post) => (
            <BlogPostCard key={post.id} post={post} onUpdated={update} onDeleted={remove} />
          ))}
        </div>
      )}
    </>
  )
}
