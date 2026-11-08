export function List({ user }: { user: { name: string } }) {
  return (
    <ul>
      <>{user.name}'s items</>
      <li>Ship it — today</li>
    </ul>
  )
}

// @ts-ignore
