'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '@/lib/api'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Dialog } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { useToastStore } from '@/stores/toast-store'
import { UserPlus, Trash2, Mail } from 'lucide-react'
import type { BrandMember } from '@vfs/shared-types'

export default function MembersPage() {
  const [showInvite, setShowInvite] = useState(false)
  const [email, setEmail] = useState('')
  const [role, setRole] = useState<'admin' | 'member'>('member')
  const { addToast } = useToastStore()
  const queryClient = useQueryClient()

  const brandId = '' // Should come from auth/brand context

  const { data: members, isLoading } = useQuery({
    queryKey: ['brand-members'],
    queryFn: async () => {
      const res = await api.get<BrandMember[]>('/brands/me')
      return res.data
    },
  })

  const inviteMutation = useMutation({
    mutationFn: async (email: string) => {
      return api.post(`/brands/${brandId}/members`, { email, role })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brand-members'] })
      setShowInvite(false)
      setEmail('')
      addToast({ type: 'success', title: 'Membre ajouté' })
    },
  })

  const removeMutation = useMutation({
    mutationFn: async (userId: string) => {
      return api.delete(`/brands/${brandId}/members/${userId}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['brand-members'] })
      addToast({ type: 'success', title: 'Membre retiré' })
    },
  })

  return (
    <div className="animate-fade-in">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-display text-3xl tracking-tight text-text-primary">Membres</h1>
          <p className="mt-1 text-text-secondary">Gérez votre équipe</p>
        </div>
        <Button size="sm" iconLeft={<UserPlus className="h-3.5 w-3.5" />} onClick={() => setShowInvite(true)}>
          Inviter
        </Button>
      </div>

      <Card>
        {isLoading ? (
          <div className="py-12 text-center text-sm text-text-secondary">Chargement...</div>
        ) : (
          <div>
            {(members?.data || []).map((member: BrandMember) => (
              <div
                key={member.user_id}
                className="flex items-center justify-between border-b border-border-subtle px-4 py-3 last:border-0"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-bg-elevated text-xs font-medium text-text-primary">
                    {(member as any).email?.[0] || '?'}
                  </div>
                  <div>
                    <p className="text-sm text-text-primary">{(member as any).email || member.user_id}</p>
                    <Badge status={member.role === 'admin' ? 'active' : 'default'} className="text-2xs">
                      {member.role === 'admin' ? 'Admin' : 'Membre'}
                    </Badge>
                  </div>
                </div>
                {member.role !== 'admin' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeMutation.mutate(member.user_id)}
                    className="text-status-error"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
            {(!members?.data || members.data.length === 0) && (
              <div className="py-12 text-center">
                <Mail className="mx-auto h-8 w-8 text-text-tertiary" />
                <p className="mt-3 text-sm text-text-secondary">
                  Invitez des membres de votre équipe
                </p>
              </div>
            )}
          </div>
        )}
      </Card>

      <Dialog open={showInvite} onClose={() => setShowInvite(false)} title="Inviter un membre">
        <div className="space-y-4">
          <div>
            <label className="mb-1 block text-xs text-text-secondary">Email</label>
            <Input
              type="email"
              placeholder="collaborateur@marque.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-text-secondary">Rôle</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as 'admin' | 'member')}
              className="w-full rounded-md border border-border-default bg-bg-surface px-3 py-2 text-sm text-text-primary"
            >
              <option value="member">Membre</option>
              <option value="admin">Admin</option>
            </select>
          </div>
          <Button
            className="w-full"
            loading={inviteMutation.isPending}
            disabled={!email.trim()}
            onClick={() => inviteMutation.mutate(email)}
          >
            Inviter
          </Button>
        </div>
      </Dialog>
    </div>
  )
}
