import { create } from 'zustand'
import type { GarmentCategory, JobStatus } from '@vfs/shared-types'

interface StudioState {
  activePhoto: { url: string; r2_key: string } | null
  selectedGarment: {
    id?: string
    image_url: string
    name?: string
    category: GarmentCategory
  } | null
  selectedCategory: GarmentCategory | null
  currentJobId: string | null
  jobStatus: JobStatus | null
  resultUrl: string | null
  resultMetadata: Record<string, unknown> | null
  errorMessage: string | null
  isGenerating: boolean

  setActivePhoto: (photo: { url: string; r2_key: string } | null) => void
  setSelectedGarment: (garment: StudioState['selectedGarment']) => void
  setCategory: (category: GarmentCategory) => void
  setJobId: (jobId: string) => void
  setJobStatus: (status: JobStatus) => void
  setResult: (url: string, metadata?: Record<string, unknown>) => void
  setError: (message: string) => void
  reset: () => void
}

const initialState = {
  activePhoto: null,
  selectedGarment: null,
  selectedCategory: null,
  currentJobId: null,
  jobStatus: null,
  resultUrl: null,
  resultMetadata: null,
  errorMessage: null,
  isGenerating: false,
}

export const useStudioStore = create<StudioState>((set) => ({
  ...initialState,

  setActivePhoto: (photo) => set({ activePhoto: photo }),
  setSelectedGarment: (garment) => set({ selectedGarment: garment }),
  setCategory: (category) => set({ selectedCategory: category }),
  setJobId: (jobId) =>
    set({ currentJobId: jobId, isGenerating: true, errorMessage: null }),
  setJobStatus: (status) => set({ jobStatus: status }),
  setResult: (url, metadata) =>
    set({
      resultUrl: url,
      resultMetadata: metadata || null,
      jobStatus: 'done',
      isGenerating: false,
    }),
  setError: (message) =>
    set({
      errorMessage: message,
      jobStatus: 'error',
      isGenerating: false,
    }),
  reset: () => set(initialState),
}))
