import type { ActivityItem } from "../types/system";

type ActivityFeedProps = {
  items: ActivityItem[];
};

export function ActivityFeed({ items }: ActivityFeedProps) {
  return (
    <section className="activity-feed" aria-labelledby="activity-title">
      <div className="section-heading">
        <p className="eyebrow">Today</p>
        <h2 id="activity-title">Activity</h2>
      </div>
      <ol>
        {items.map((item) => (
          <li key={item.id}>
            <span>{item.time}</span>
            <div>
              <strong>{item.title}</strong>
              <p>{item.detail}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}
